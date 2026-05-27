# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Authroization API service.

This module is the API for the Authroization system.
"""

import os
import threading
import traceback

import grpc
from cloud_sql_connector import DBConfig, setup_search_path_event_listener
from flask import Flask, request  # noqa: TC002
from flask_cors import CORS
from flask_migrate import Migrate, upgrade
from google.auth import default as google_auth_default
from google.auth.transport.grpc import AuthMetadataPlugin
from google.auth.transport.requests import Request as GoogleAuthRequest
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sbc_common_components.utils.camel_case_response import convert_to_camel

import auth_api.config as config  # pylint:disable=consider-using-from-import
from auth_api.config import _Config
from auth_api.exceptions import ExceptionHandler
from auth_api.extensions import mail
from auth_api.models import db, ma
from auth_api.resources import endpoints
from auth_api.services.flags import flags
from auth_api.services.gcp_queue import queue
from auth_api.utils.auth import jwt
from auth_api.utils.cache import cache
from auth_api.utils.logging import setup_logging
from auth_api.utils.user_context import _get_context

setup_logging(os.path.join(_Config.PROJECT_ROOT, "logging.conf"))


def create_app(run_mode=None):
    """Return a configured Flask App using the Factory method."""
    if run_mode is None:
        run_mode = os.getenv("DEPLOYMENT_ENV", "production")
    app = Flask(__name__)
    app.config["ENV"] = run_mode
    app.config.from_object(config.CONFIGURATION[run_mode])

    schema = app.config.get("DB_SCHEMA", "public")

    CORS(app, resources="*")

    if app.config.get("DB_INSTANCE_CONNECTION_NAME"):
        db_config = DBConfig(
            instance_name=app.config.get("DB_INSTANCE_CONNECTION_NAME"),
            database=app.config.get("DB_NAME"),
            user=app.config.get("DB_USER"),
            ip_type=app.config.get("DB_IP_TYPE"),
            schema=schema if run_mode != "migration" else None,
            pool_recycle=300,
        )

        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = db_config.get_engine_options()

    db.init_app(app)

    if run_mode != "migration":
        with app.app_context():
            engine = db.engine
            setup_search_path_event_listener(engine, schema)

    if run_mode == "migration":
        Migrate(app, db)
        app.logger.info("Running migration upgrade.")
        with app.app_context():
            execute_migrations(app)
        # Alembic has it's own logging config, we'll need to restore our logging here.
        setup_logging(os.path.join(_Config.PROJECT_ROOT, "logging.conf"))
        app.logger.info("Finished migration upgrade.")
        app.logger.info("Note: endpoints will 404 until the DEPLOYMENT_ENV is switched off of migration.")
    else:
        flags.init_app(app)
        ma.init_app(app)
        queue.init_app(app)
        mail.init_app(app)
        endpoints.init_app(app)

        app.after_request(convert_to_camel)

        ExceptionHandler(app)
        setup_tracing(app)
        setup_403_logging(app)
        setup_jwt_manager(app, jwt)
        register_shellcontext(app)
        build_cache(app)

    return app


def setup_tracing(app):
    """Set up OTEL tracing with OTLP/gRPC export to Google Cloud Trace.

    Controlled via OTEL_SDK_DISABLED in config.py (default: True).
    Override per environment via op://relationship/$APP_ENV/auth-api/OTEL_SDK_DISABLED in vaults.gcp.env.
    """
    if app.config.get("OTEL_SDK_DISABLED", True):
        return

    credentials, _ = google_auth_default()
    channel_credentials = grpc.composite_channel_credentials(
        grpc.ssl_channel_credentials(),
        grpc.metadata_call_credentials(AuthMetadataPlugin(credentials, GoogleAuthRequest())),
    )
    exporter = OTLPSpanExporter(
        endpoint="telemetry.googleapis.com:443",
        credentials=channel_credentials,
    )
    provider = TracerProvider(resource=Resource.create())
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FlaskInstrumentor().instrument_app(app)
    with app.app_context():
        SQLAlchemyInstrumentor().instrument(engine=db.engine)
    RequestsInstrumentor().instrument()

    @app.before_request
    def attach_frontend_trace_id():
        registries_trace_id = request.headers.get("registries-trace-id")
        if registries_trace_id:
            span = trace.get_current_span()
            if span.is_recording():
                span.set_attribute("app.registries_trace_id", registries_trace_id)


def setup_403_logging(app):
    """Log setup for forbidden."""
    if app.config.get("ENABLE_403_LOGGING") is True:

        @app.errorhandler(403)
        def handle_403_error(error):
            user_context = _get_context()

            user_name = user_context.user_name[:5] + "..."
            roles = user_context.roles
            app.logger.error(f"403 Forbidden - {request.method} {request.url} - {user_name} - {roles}")

            message = {"message": getattr(error, "message", error.description)}
            headers = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}
            return message, error.code, headers


def execute_migrations(app):
    """Execute the database migrations."""
    try:
        upgrade(directory="migrations", revision="head", sql=False, tag=None)
    except Exception as e:  # NOQA pylint: disable=broad-except
        app.logger.disabled = False
        error_message = f"Error processing migrations: {e}\n{traceback.format_exc()}"
        app.logger.error(error_message)
        raise e


def setup_jwt_manager(app, jwt_manager):
    """Use flask app to configure the JWTManager to work for a particular Realm."""

    def get_roles(a_dict):
        return a_dict["realm_access"]["roles"]  # pragma: no cover

    app.config["JWT_ROLE_CALLBACK"] = get_roles

    jwt_manager.init_app(app)


def register_shellcontext(app):
    """Register shell context objects."""
    from auth_api import models  # pylint: disable=import-outside-toplevel

    def shell_context():
        """Shell context objects."""
        return {"app": app, "jwt": jwt, "db": db, "models": models}  # pragma: no cover

    app.shell_context_processor(shell_context)


def build_cache(app):
    """Build cache in a background thread so gunicorn can start accepting requests immediately."""
    cache.init_app(app)

    if app.config.get("TESTING", False):
        return

    def _build():
        with app.app_context():
            try:
                # pylint: disable=import-outside-toplevel
                from auth_api.services.permissions import Permissions as PermissionService
                from auth_api.services.products import Product as ProductService

                cache.clear()
                PermissionService.build_all_permission_cache()
                ProductService.build_all_products_cache()
                app.logger.info("Cache build complete.")
            except Exception as e:  # NOQA # pylint:disable=broad-except
                app.logger.error(f"Error on caching {e}")

    threading.Thread(target=_build, daemon=True).start()

# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Resource package for the auth-queue service."""
import os

from auth_api.exceptions import ExceptionHandler
from auth_api.models import db
from auth_api.resources.ops import bp as ops_bp
from auth_api.services.flags import flags
from auth_api.services.gcp_queue import queue
from auth_api.utils.cache import cache
from auth_api.utils.logging import setup_logging
from cloud_sql_connector import DBConfig, setup_search_path_event_listener
from flask import Flask
from google.cloud.sql.connector import Connector

from auth_queue import config as app_config
from auth_queue.resources.worker import bp as worker_endpoint

setup_logging(os.path.join(os.path.abspath(os.path.dirname(__file__)), "logging.conf"))  # important to do this first


def register_endpoints(app: Flask):
    """Register endpoints with the flask application."""
    # Allow base route to match with, and without a trailing slash
    app.url_map.strict_slashes = False

    app.register_blueprint(
        url_prefix="/",
        blueprint=worker_endpoint,
    )
    app.register_blueprint(ops_bp)


def create_app(run_mode=os.getenv("DEPLOYMENT_ENV", "production")) -> Flask:
    """Return a configured Flask App using the Factory method."""
    app = Flask(__name__)
    app.config.from_object(app_config.get_named_config(run_mode))
    app.config["ENV"] = run_mode
    schema = app.config.get("DB_SCHEMA", "public")

    if app.config.get("DB_INSTANCE_CONNECTION_NAME"):
        db_config = DBConfig(
            instance_name=app.config.get("DB_INSTANCE_CONNECTION_NAME"),
            database=app.config.get("DB_NAME"),
            user=app.config.get("DB_USER"),
            ip_type=app.config.get("DB_IP_TYPE"),
            schema=schema,
            pool_recycle=300,
        )

        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = db_config.get_engine_options()

    db.init_app(app)

    if app.config.get("DB_INSTANCE_CONNECTION_NAME"):
        with app.app_context():
            engine = db.engine
            setup_search_path_event_listener(engine, schema)

    flags.init_app(app)
    cache.init_app(app)
    queue.init_app(app)

    register_endpoints(app)
    ExceptionHandler(app)

    return app

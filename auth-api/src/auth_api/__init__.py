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

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate, upgrade

import auth_api.config as config  # pylint:disable=consider-using-from-import
from auth_api.config import _Config
from auth_api.extensions import mail
from auth_api.models import db, ma
from auth_api.resources import endpoints
from auth_api.services.flags import flags
from auth_api.services.gcp_queue import queue
from auth_api.utils.auth import jwt
from auth_api.utils.cache import cache
from auth_api.utils.util_logging import setup_logging

setup_logging(os.path.join(_Config.PROJECT_ROOT, "logging.conf"))


def create_app(run_mode=os.getenv("DEPLOYMENT_ENV", "production")):
    """Return a configured Flask App using the Factory method."""
    app = Flask(__name__)
    app.env = run_mode
    app.config.from_object(config.CONFIGURATION[run_mode])

    CORS(app, resources="*")

    flags.init_app(app)
    db.init_app(app)

    if run_mode != "testing":
        Migrate(app, db)
        app.logger.info("Running migration upgrade.")
        with app.app_context():
            execute_migrations(app)

    # Alembic has it's own logging config, we'll need to restore our logging here.
    setup_logging(os.path.join(_Config.PROJECT_ROOT, "logging.conf"))
    app.logger.info("Finished migration upgrade.")

    ma.init_app(app)
    queue.init_app(app)
    mail.init_app(app)
    endpoints.init_app(app)

    setup_jwt_manager(app, jwt)
    register_shellcontext(app)
    build_cache(app)

    return app


def execute_migrations(app):
    """Execute the database migrations."""
    try:
        upgrade(directory="migrations", revision="head", sql=False, tag=None)
    except Exception as e:  # NOQA pylint: disable=broad-except
        app.logger.disabled = False
        app.logger.error("Error processing migrations:", exc_info=True)
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
    """Build cache."""
    cache.init_app(app)
    with app.app_context():
        cache.clear()
        if not app.config.get("TESTING", False):
            try:
                from auth_api.services.permissions import (  # pylint: disable=import-outside-toplevel
                    Permissions as PermissionService,
                )
                from auth_api.services.products import (  # pylint: disable=import-outside-toplevel
                    Product as ProductService,
                )

                PermissionService.build_all_permission_cache()
                ProductService.build_all_products_cache()
            except Exception as e:  # NOQA # pylint:disable=broad-except
                app.logger.error("Error on caching ")
                app.logger.error(e)

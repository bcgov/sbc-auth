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
from dataclasses import dataclass

from auth_api.exceptions import ExceptionHandler
from auth_api.models import db
from auth_api.resources.ops import bp as ops_bp
from auth_api.services.flags import flags
from auth_api.services.gcp_queue import queue
from auth_api.utils.cache import cache
from flask import Flask
from google.cloud.sql.connector import Connector

from auth_queue import config as app_config
from auth_queue.resources.worker import bp as worker_endpoint


@dataclass
class DBConfig:
    """Database configuration settings."""

    unix_sock: str
    database: str
    user: str
    password: str


def getconn(connector: Connector, db_config: DBConfig) -> object:
    """Create a database connection.

    Args:
        connector (Connector): The Google Cloud SQL connector instance.
        db_config (DBConfig): The database configuration.
    Returns:
        object: A connection object to the database.
    """
    return connector.connect(
        instance_connection_string=db_config.unix_sock.replace('/cloudsql/', ''),
        ip_type='private',
        user=db_config.user,
        password=db_config.password,
        db=db_config.database,
        driver='pg8000',
    )


def register_endpoints(app: Flask):
    """Register endpoints with the flask application."""
    # Allow base route to match with, and without a trailing slash
    app.url_map.strict_slashes = False

    app.register_blueprint(
        url_prefix='/',
        blueprint=worker_endpoint,
    )
    app.register_blueprint(ops_bp)


def create_app(run_mode=os.getenv('DEPLOYMENT_ENV', 'production')) -> Flask:
    """Return a configured Flask App using the Factory method."""
    app = Flask(__name__)
    app.config.from_object(app_config.get_named_config(run_mode))
    app.config['ENV'] = run_mode

    if app.config.get('DB_UNIX_SOCKET'):
        connector = Connector(refresh_strategy='lazy')
        db_config = DBConfig(
            unix_sock=app.config.get('DB_UNIX_SOCKET'),
            database=app.config.get('DB_NAME'),
            user=app.config.get('DB_USER'),
            password=app.config.get('DB_PASSWORD')
        )
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'creator': lambda: getconn(connector, db_config)
        }

    db.init_app(app)
    flags.init_app(app)
    cache.init_app(app)
    queue.init_app(app)

    register_endpoints(app)
    ExceptionHandler(app)

    return app

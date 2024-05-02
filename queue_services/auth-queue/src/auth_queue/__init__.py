# Copyright © 2019 Province of British Columbia
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

import sentry_sdk
from auth_api.models import db
from auth_api.resources.ops import bp as ops_bp
from auth_api.services.flags import flags
from auth_api.services.gcp_queue import queue
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration

from auth_queue import config
from auth_queue.resources.worker import bp as worker_endpoint


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
    app.config.from_object(config.get_named_config(run_mode))

    if str(app.config.get('SENTRY_ENABLE')).lower() == 'true':
        if app.config.get('SENTRY_DSN', None):
            sentry_sdk.init(  # pylint: disable=abstract-class-instantiated
                dsn=app.config.get('SENTRY_DSN'),
                integrations=[FlaskIntegration()]
            )

    db.init_app(app)
    flags.init_app(app)
    queue.init_app(app)

    register_endpoints(app)

    return app

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
"""The Status API service.

This module is the API for the Entity system.
"""
import os

import sentry_sdk
from flask import Flask
from sbc_common_components.exception_handling.exception_handler import ExceptionHandler  # noqa: I001
from sbc_common_components.utils.camel_case_response import convert_to_camel
from sentry_sdk.integrations.flask import FlaskIntegration  # pylint: disable=ungrouped-imports

from config import CONFIGURATION, _Config  # pylint: disable=import-error
from status_api import models
from status_api.utils.run_version import get_run_version
from status_api.utils.util_logging import setup_logging


setup_logging(os.path.join(_Config.PROJECT_ROOT, 'logging.conf'))  # important to do this first


def create_app(run_mode=os.getenv('FLASK_ENV', 'production')):
    """Return a configured Flask App using the Factory method."""
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(CONFIGURATION[run_mode])

    # Configure Sentry
    if app.config.get('SENTRY_ENABLE') == 'True':
        if app.config.get('SENTRY_DSN', None):
            sentry_sdk.init(
                dsn=app.config.get('SENTRY_DSN'),
                integrations=[FlaskIntegration()]
            )

    from status_api.resources import API_BLUEPRINT, OPS_BLUEPRINT  # pylint: disable=import-outside-toplevel

    app.register_blueprint(API_BLUEPRINT)
    app.register_blueprint(OPS_BLUEPRINT)
    app.after_request(convert_to_camel)

    ExceptionHandler(app)

    @app.after_request
    def add_version(response):  # pylint: disable=unused-variable
        version = get_run_version()
        response.headers['API'] = f'status_api/{version}'
        return response

    register_shellcontext(app)

    return app


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {'app': app, 'models': models}  # pragma: no cover

    app.shell_context_processor(shell_context)

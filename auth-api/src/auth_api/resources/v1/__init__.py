# Copyright © 2023 Province of British Columbia
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
"""Exposes all of the resource endpoints mounted in Flask-Blueprints."""
from typing import Optional

from flask import Flask

from ..account import bp as accounts_bp
from ..acitivity_log import bp as activity_log_bp
from ..affiliation_invitation import bp as affiliation_invitation_bp
from ..bcol_profiles import bp as bcol_profiles_bp
from ..bulk_user import bp as bulk_user_bp
from ..codes import bp as codes_bp
from ..documents import bp as documents_bp
from ..documents_affidavit import bp as documents_affidavit_bp
from ..entity import bp as entity_bp
from ..invitation import bp as invitation_bp
from ..meta import bp as meta_bp
from ..notifications import bp as notifications_bp
from ..ops import bp as ops_bp
from ..org import bp as org_bp
from ..org_api_keys import bp as org_api_keys_bp
from ..org_authorizations import bp as org_authorizations_bp
from ..org_products import bp as org_products_bp
from ..permissions import bp as permissions_bp
from ..products import bp as products_bp
from ..task import bp as task_bp
from ..user import bp as user_bp
from ..user_settings import bp as user_settings_bp


class V1Endpoint:  # pylint: disable=too-few-public-methods,
    """Setup all the V1 Endpoints."""

    def __init__(self):
        """Create the endpoint setup, without initializations."""
        self.app: Optional[Flask] = None

    def init_app(self, app):
        """Register and initialize the Endpoint setup."""
        if not app:
            raise Exception('Cannot initialize without a Flask App.')  # pylint: disable=broad-exception-raised

        self.app = app
        self.app.register_blueprint(accounts_bp)
        self.app.register_blueprint(activity_log_bp)
        self.app.register_blueprint(affiliation_invitation_bp)
        self.app.register_blueprint(bcol_profiles_bp)
        self.app.register_blueprint(bulk_user_bp)
        self.app.register_blueprint(codes_bp)
        self.app.register_blueprint(documents_bp)
        self.app.register_blueprint(documents_affidavit_bp)
        self.app.register_blueprint(entity_bp)
        self.app.register_blueprint(invitation_bp)
        self.app.register_blueprint(meta_bp)
        self.app.register_blueprint(notifications_bp)
        self.app.register_blueprint(ops_bp)
        self.app.register_blueprint(org_bp)
        self.app.register_blueprint(org_api_keys_bp)
        self.app.register_blueprint(org_authorizations_bp)
        self.app.register_blueprint(org_products_bp)
        self.app.register_blueprint(permissions_bp)
        self.app.register_blueprint(products_bp)
        self.app.register_blueprint(task_bp)
        self.app.register_blueprint(user_bp)
        self.app.register_blueprint(user_settings_bp)


v1_endpoint = V1Endpoint()

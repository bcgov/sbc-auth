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
"""API endpoints for managing a Product resource."""

from flask import request
from flask_restx import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.services.authorization import Authorization as AuthorizationService
from auth_api.tracer import Tracer
from auth_api.utils.util import cors_preflight


API = Namespace('permissions', description='Endpoints for permissions management')
TRACER = Tracer.get_instance()


@cors_preflight('GET,OPTIONS')
@API.route('', methods=['GET', 'OPTIONS'])
class OrgAuthorizationResource(Resource):
    """Resource for managing entity authorizations."""

    @staticmethod
    @_jwt.requires_auth
    @cors.crossdomain(origin='*')
    def get(org_id):
        """Return authorization for the user for the passed business identifier."""
        expanded: bool = request.args.get('expanded', False)
        corp_type_code = request.headers.get('Product-Code', None)
        authorisations = AuthorizationService.get_account_authorizations_for_org(org_id, corp_type_code, expanded)
        return authorisations, http_status.HTTP_200_OK

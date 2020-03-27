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
"""API endpoints for managing an Org resource."""

from flask import g, request
from flask_restplus import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.services.authorization import Authorization as AuthorizationService
from auth_api.tracer import Tracer
from auth_api.utils.util import cors_preflight

API = Namespace('accounts', description='Endpoints for accounts management')

TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET,OPTIONS')
@API.route('/<string:account_id>/products/<string:product_code>/authorizations', methods=['GET', 'OPTIONS'])
class AccountAuthorizations(Resource):
    """Resource for returning authorizations for a product in an account."""

    @staticmethod
    @_JWT.requires_auth
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get(account_id, product_code):
        """Return authorizations for a product in an account."""
        expanded: bool = request.args.get('expanded', False)
        authorizations = AuthorizationService.get_account_authorizations_for_product(
            g.jwt_oidc_token_info.get('sub', None),
            account_id, product_code, expanded)
        return authorizations, http_status.HTTP_200_OK

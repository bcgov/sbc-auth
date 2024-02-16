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

from flask import Blueprint, request
from flask_cors import cross_origin
from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.services.authorization import Authorization as AuthorizationService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum

bp = Blueprint('ACCOUNTS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/accounts')
TRACER = Tracer.get_instance()


@bp.route('/<int:account_id>/products/<string:product_code>/authorizations', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET'])
@TRACER.trace()
@_jwt.requires_auth
def get_account_product_authorizations(account_id, product_code):
    """Return authorizations for a product in an account."""
    expanded: bool = request.args.get('expanded', False)
    authorizations = AuthorizationService.get_account_authorizations_for_product(account_id, product_code, expanded)
    return authorizations, http_status.HTTP_200_OK

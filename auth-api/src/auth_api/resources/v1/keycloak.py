"""Keycloak resource, will ultimately get swapped out."""
# Copyright © 2024 Province of British Columbia
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

# Note this will be depreciated and replaced shortly.

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import Role

bp = Blueprint('KEYCLOAK', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/keycloak')

@bp.route('/users', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET'])
@_jwt.has_one_of_roles([Role.SYSTEM.value])
def get_keycloak_users_by_role():
    """Return keycloak name + email by role."""
    role = request.args.get('role', None)
    if role is None:
        response, status = {'message': 'Role query parameter is required'}, http_status.HTTP_400_BAD_REQUEST
    try:
        response, status = KeycloakService.get_user_emails_with_role(role), http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return jsonify(response), status

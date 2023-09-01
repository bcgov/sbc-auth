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
"""API endpoints for managing an API gateway keys for org."""

from flask import Blueprint, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.schemas import utils as schema_utils
from auth_api.services import ApiGateway as ApiGatewayService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import Role

bp = Blueprint('KEYS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/orgs/<int:org_id>/api-keys')
TRACER = Tracer.get_instance()


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET', 'POST'])
@TRACER.trace()
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.ACCOUNT_HOLDER.value])
def get_organization_api_keys(org_id):
    """Get all API keys for the account."""
    return ApiGatewayService.get_api_keys(org_id), http_status.HTTP_200_OK


@bp.route('', methods=['POST'])
@cross_origin(origins='*')
@TRACER.trace()
@_jwt.has_one_of_roles([Role.SYSTEM.value])
def post_organization_api_key(org_id):
    """Create new api key for the org."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, 'api_key')

    if not valid_format:
        return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST
    try:
        response, status = ApiGatewayService.create_key(org_id, request_json), http_status.HTTP_201_CREATED
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<string:key>', methods=['DELETE', 'OPTIONS'])
@cross_origin(origins='*', methods=['DELETE'])
@TRACER.trace()
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.ACCOUNT_HOLDER.value])
def delete_organization_api_key(org_id, key):
    """Revoke API Key."""
    try:
        ApiGatewayService.revoke_key(org_id, key)
        response, status = {}, http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status

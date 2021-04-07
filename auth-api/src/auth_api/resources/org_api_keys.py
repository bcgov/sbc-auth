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

from flask import request
from flask_restplus import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.auth import jwt as _jwt
from auth_api.schemas import utils as schema_utils
from auth_api.services import ApiGateway as ApiGatewayService
from auth_api.tracer import Tracer
from auth_api.utils.roles import Role
from auth_api.utils.util import cors_preflight

API = Namespace('keys', description='Endpoints for API Keys management')
TRACER = Tracer.get_instance()


@cors_preflight('POST,GET,OPTIONS')
@API.route('', methods=['POST', 'GET', 'OPTIONS'])
class OrgKeys(Resource):
    """Resource for managing API gw keys."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.has_one_of_roles([Role.SYSTEM.value])
    def get(org_id):
        """Get all API keys for the account."""
        return ApiGatewayService.get_api_keys(org_id), http_status.HTTP_200_OK

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.has_one_of_roles([Role.SYSTEM.value])
    def post(org_id):
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


@cors_preflight('DELETE,OPTIONS')
@API.route('/<string:key>', methods=['DELETE', 'OPTIONS'])
class OrgKey(Resource):
    """Resource for managing API gateway key."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.has_one_of_roles([Role.SYSTEM.value])
    def delete(org_id, key):
        """Revoke API Key."""
        try:
            ApiGatewayService.revoke_key(org_id, key)
            response, status = {}, http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

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
"""API endpoints for managing a User resource."""

from flask import request, g
from flask_restplus import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.schemas import utils as schema_utils
from auth_api.services.user import User as UserService
from auth_api.tracer import Tracer
from auth_api.utils.util import cors_preflight

API = Namespace('bulk users', description='Endpoints for bulk user profile management')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class BulkUser(Resource):
    """Resource for managing bulk  users post."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def post():
        """Admin users can post multiple users to his org.Use it for anonymous purpose only."""
        try:
            request_json = request.get_json()
            valid_format, errors = schema_utils.validate(request_json, 'bulk_user')
            token = g.jwt_oidc_token_info
            if not valid_format:
                return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

            users = UserService.create_user_and_add_membership(request_json['users'],
                                                               request_json['orgId'], token)
            response, status = users, http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

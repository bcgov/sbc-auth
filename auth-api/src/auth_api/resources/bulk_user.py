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

from flask import Blueprint, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.schemas import utils as schema_utils
from auth_api.services.user import User as UserService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum


bp = Blueprint('BULK_USERS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/bulk/users')
TRACER = Tracer.get_instance()


@bp.route('', methods=['POST', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def post_bulk_users():
    """Admin users can post multiple users to his org.Use it for anonymous purpose only."""
    try:
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'bulk_user')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        users = UserService.create_user_and_add_membership(request_json['users'], request_json['orgId'])
        is_any_error = any(user['http_status'] != 201 for user in users['users'])

        response, status = users, http_status.HTTP_207_MULTI_STATUS if is_any_error else http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status

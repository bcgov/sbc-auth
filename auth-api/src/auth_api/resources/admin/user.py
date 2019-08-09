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

from flask import g, request
from flask_jwt_oidc import AuthError
from flask_restplus import Namespace, Resource, cors
from sqlalchemy import exc

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.services.user import User as UserService
from auth_api.tracer import Tracer
from auth_api.utils.roles import Role
from auth_api.utils.util import cors_preflight


API = Namespace('users', description='User')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET, POST, PATCH, DELETE')
@API.route('', methods=['POST'])
class Users(Resource):
    """Resource for managing users."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def post():
        """Post a new user using the request body (which will contain a JWT).

        If the user already exists, update the name.
        """
        token = g.jwt_oidc_token_info
        if not token:
            return {'message': 'No valid token provided.'}, http_status.HTTP_400_BAD_REQUEST

        try:
            response, status = UserService.save_from_jwt_token(token).as_dict(), http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        except exc.IntegrityError:
            response, status = {'message': 'That user already exists'}, http_status.HTTP_409_CONFLICT
        return response, status

    # @staticmethod
    # @TRACER.trace()
    # def get():
    #     """Returns a set of users based on search query parameter."""
    #     search_email = request.args.get('email')
    #     search_name = request.args.get('name')

    #     UserService.

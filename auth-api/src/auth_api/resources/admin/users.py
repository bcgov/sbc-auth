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
"""Endpoints to to manage user."""

from flask import request, jsonify
from flask_restplus import Resource, Namespace
from flask_jwt_oidc import AuthError

from auth_api import tracing as _tracing
from auth_api import status as http_status

from auth_api.services.keycloak import KeycloakService
from auth_api.utils.util import cors_preflight
from auth_api.exceptions import BusinessException
from auth_api.exceptions import catch_business_exception

API = Namespace('admin/users', description='Keycloak Admin - user')
KEYCLOAK_SERVICE = KeycloakService()


@API.errorhandler(AuthError)
def handle_auth_error(exception):
    """TODO just a demo function"""
    return jsonify(exception), exception.status_code


@API.errorhandler(BusinessException)
def handle_db_exception(error):
    """TODO just a demo function"""
    return {'error': '{}'.format(error.code), 'message': '{}'.format(error.error),
            'detail': '{}'.format(error.detail)}, error.status_code


@API.errorhandler(Exception)
def handle_exception(exception):
    """TODO just a demo function"""
    return {'error': '{}'.format(exception.code), 'message': '{}'.format(exception.error),
            'detail': '{}'.format(exception.detail)}, exception.status_code


@cors_preflight('GET, POST, DELETE, OPTIONS')
@API.route('', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
class User(Resource):
    """End point resource to manage users."""

    @staticmethod
    @_tracing.trace()
    @catch_business_exception
    #@_jwt.has_one_of_roles([Role.ADMIN.value])
    #@_jwt.requires_auth
    def post():
        """Add user, return a new/existing user."""

        data = request.get_json()
        if not data:
            data = request.values
        try:
            response = KEYCLOAK_SERVICE.add_user(data)

            return response, http_status.HTTP_201_CREATED
        except BusinessException as err:
            return {'error': '{}'.format(err.code), 'message': '{}'.format(err.error),
                    'detail': '{}'.format(err.detail)}, err.status_code

    @staticmethod
    @_tracing.trace()
    def get():
        """Get user by username and return a user"""

        data = request.get_json()
        if not data:
            data = request.values
        try:
            user = KEYCLOAK_SERVICE.get_user_by_username(data.get('username'))
            return user, http_status.HTTP_200_OK
        except BusinessException as err:
            return {'error': '{}'.format(err.code), 'message': '{}'.format(err.error),
                    'detail': '{}'.format(err.detail)}, err.status_code

    @staticmethod
    @_tracing.trace()
    def delete():
        """Delete user by username"""

        data = request.get_json()
        if not data:
            data = request.values
        try:
            response = KEYCLOAK_SERVICE.delete_user_by_username(data.get('username'))
            return response, http_status.HTTP_204_NO_CONTENT
        except BusinessException as err:
            return {'error': '{}'.format(err.code), 'message': '{}'.format(err.error),
                    'detail': '{}'.format(err.detail)}, err.status_code

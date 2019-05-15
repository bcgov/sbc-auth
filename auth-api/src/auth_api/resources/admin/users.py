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

from flask import request
from flask_restplus import Resource, Namespace

from auth_api import tracing as _tracing
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.util import cors_preflight

API = Namespace('admin/users', description='Keycloak Admin - user')
KEYCLOAK_SERVICE = KeycloakService()


@cors_preflight('GET, POST, DELETE, OPTIONS')
@API.route('', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
class User(Resource):
    """End point resource to manage users."""

    @staticmethod
    @_tracing.trace()
    def post():
        """Add user, return a new/existing user."""

        data = request.get_json()
        if not data:
            data = request.values

        response = KEYCLOAK_SERVICE.add_user(data)

        return response, 201

    @staticmethod
    @_tracing.trace()
    def get():
        """Get user by username and return a user"""

        data = request.get_json()
        if not data:
            data = request.values
        user = KEYCLOAK_SERVICE.get_user_by_username(data.get('username'))
        return user, 200

    @staticmethod
    @_tracing.trace()
    def delete():
        """Delete user by username"""

        data = request.get_json()
        if not data:
            data = request.values
        response = KEYCLOAK_SERVICE.delete_user_by_username(data.get('username'))
        return response, 204

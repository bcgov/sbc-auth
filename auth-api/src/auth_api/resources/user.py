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

from flask import g, jsonify, request
from flask_restplus import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.schemas import utils as schema_utils
from auth_api.services.authorization import Authorization as AuthorizationService
from auth_api.services.user import User as UserService
from auth_api.tracer import Tracer
from auth_api.utils.roles import Role
from auth_api.utils.util import cors_preflight


API = Namespace('users', description='Endpoints for user profile management')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET,POST,OPTIONS')
@API.route('', methods=['GET', 'POST', 'OPTIONS'])
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
            return {'message': 'Authorization required.'}, http_status.HTTP_401_UNAUTHORIZED

        try:
            response, status = UserService.save_from_jwt_token(token).as_dict(), http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.STAFF.value])
    def get():
        """Return a set of users based on search query parameters (staff only)."""
        search_email = request.args.get('email', '')
        search_first_name = request.args.get('firstname', '')
        search_last_name = request.args.get('lastname', '')

        users = UserService.find_users(first_name=search_first_name, last_name=search_last_name, email=search_email)
        collection = []
        for user in users:
            collection.append(UserService(user).as_dict())
        response = jsonify(collection)
        status = http_status.HTTP_200_OK
        return response, status


@cors_preflight('GET,OPTIONS')
@API.route('/<string:username>', methods=['GET', 'OPTIONS'])
class UserStaff(Resource):
    """Resource for managing an individual user for a STAFF user."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.STAFF.value])
    def get(username):
        """Return the user profile associated with the provided username."""
        user = UserService.find_by_username(username)
        if user is None:
            response, status = {'message': 'User {} does not exist.'.format(username)}, http_status.HTTP_404_NOT_FOUND
        else:
            response, status = user.as_dict(), http_status.HTTP_200_OK
        return response, status


@cors_preflight('GET,OPTIONS')
@API.route('/@me', methods=['GET', 'OPTIONS'])
class User(Resource):
    """Resource for managing an individual user."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def get():
        """Return the user profile associated with the JWT in the authorization header."""
        token = g.jwt_oidc_token_info
        if not token:
            return {'message': 'Authorization required.'}, http_status.HTTP_401_UNAUTHORIZED

        try:
            response, status = UserService.find_by_jwt_token(token).as_dict(), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('DELETE, POST, PUT, OPTIONS')
@API.route('/contacts', methods=['DELETE', 'POST', 'PUT', 'OPTIONS'])
class UserContacts(Resource):
    """Resource for managing user contacts."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def post():
        """Create a new contact for the user associated with the JWT in the authorization header."""
        token = g.jwt_oidc_token_info
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'contact')
        if not token:
            return {'message': 'Authorization required.'}, http_status.HTTP_401_UNAUTHORIZED
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            response, status = UserService.add_contact(token, request_json).as_dict(), http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def put():
        """Update an existing contact for the user associated with the JWT in the authorization header."""
        token = g.jwt_oidc_token_info
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'contact')
        if not token:
            return {'message': 'Authorization required.'}, http_status.HTTP_401_UNAUTHORIZED
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST
        try:
            response, status = UserService.update_contact(token, request_json).as_dict(), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def delete():
        """Delete the contact info for the user associated with the JWT in the authorization header."""
        token = g.jwt_oidc_token_info
        if not token:
            return {'message': 'Authorization required.'}, http_status.HTTP_401_UNAUTHORIZED

        try:
            response, status = UserService.delete_contact(token).as_dict(), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('GET,OPTIONS')
@API.route('/orgs', methods=['GET', 'OPTIONS'])
class UserOrgs(Resource):
    """Resource for retrieving list or orgs associated with a user."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def get():
        """Get a list of orgs that the current user is associated with."""
        token = g.jwt_oidc_token_info
        if not token:
            return {'message': 'Authorization required.'}, http_status.HTTP_401_UNAUTHORIZED

        try:
            user = UserService.find_by_jwt_token(token)
            if not user:
                response, status = {'message': 'User not found.'}, http_status.HTTP_404_NOT_FOUND
            else:
                response, status = jsonify(user.get_orgs()), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('GET,OPTIONS')
@API.route('/authorizations', methods=['GET', 'OPTIONS'])
class AuthorizationResource(Resource):
    """Resource for managing entity authorizations."""

    @staticmethod
    @_JWT.requires_auth
    @cors.crossdomain(origin='*')
    def get():
        """Add a new contact for the Entity identified by the provided id."""
        sub = g.jwt_oidc_token_info.get('sub', None)
        return AuthorizationService.get_user_authorizations(sub), http_status.HTTP_200_OK

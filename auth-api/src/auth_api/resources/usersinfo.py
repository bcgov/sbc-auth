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
"""Endpoints to get user information from token and database."""

from flask import g, jsonify
from flask_jwt_oidc import AuthError
from flask_restplus import Namespace, Resource, cors

from auth_api.exceptions import UserException, catch_custom_exception
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.services import User
from auth_api.tracer import Tracer
from auth_api.utils.util import cors_preflight


API = Namespace('users/info', description='Authentication System - get User Information')
TRACER = Tracer.get_instance()
JWT = JWTWrapper.get_instance()


@API.errorhandler(AuthError)
def handle_auth_error(exception):
    """TODO just a demo function."""
    return jsonify(exception), exception.status_code


@API.errorhandler(UserException)
def handle_db_exception(error):
    """TODO just a demo function."""
    return {'message': str(error.error)}, error.status_code


@API.errorhandler(Exception)
def handle_exception(exception):
    """TODO just a demo function."""
    return {'message': str(exception.error)}, exception.status_code


# @cors_preflight('GET')
# @API.route('')
# class UserInfo(Resource):
#     """Retrieve user detail information from token and database."""

#     @staticmethod
#     @cors.crossdomain(origin='*')
#     @TRACER.trace()
#     @catch_custom_exception
#     @JWT.requires_auth
#     def get():
#         """Return a JSON object that includes user detail information."""
#         token = g.jwt_oidc_token_info
#         user = User.find_by_jwt_token(token)
#         if not user:
#             user = User.save_from_jwt_token(token)

#         return jsonify(user.asdict()), 200

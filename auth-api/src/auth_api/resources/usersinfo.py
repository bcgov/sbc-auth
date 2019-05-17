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

from flask_restplus import Namespace, Resource, cors

from auth_api import jwt as _jwt
from auth_api import tracing as _tracing
from auth_api.exceptions import catch_custom_exception
from auth_api.services import User
from auth_api.utils.util import cors_preflight

API = Namespace('users/info', description='Authentication System - get User Information')


@cors_preflight('GET')
@API.route('')
class UserInfo(Resource):
    """Retrieve user detail information from token and database """

    @staticmethod
    @cors.crossdomain(origin='*')
    @_tracing.trace()
    @catch_custom_exception
    @_jwt.requires_auth
    def get():
        """Return a JSON object that includes user detail information"""
        token = g.jwt_oidc_token_info
        user = User.find_by_jwt_token(token)
        if not user:
            user = User.save_from_jwt_token(token)

        return jsonify(user.asdict()), 200

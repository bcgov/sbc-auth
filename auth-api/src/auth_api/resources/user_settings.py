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
import json

from flask import g
from flask_restplus import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.schemas import UserSettingsSchema
from auth_api.services.user import User as UserService
from auth_api.services.user_settings import UserSettings as UserSettingsService
from auth_api.tracer import Tracer
from auth_api.utils.util import cors_preflight


API = Namespace('users', description='Endpoints for user settings management')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET, OPTIONS')
@API.route('', methods=['GET', 'OPTIONS'])
class SettingsResource(Resource):  # pylint: disable=too-few-public-methods
    """Resource for managing a user's settings."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def get(user_id):
        """Get info related to the user.

        Currently returns the org details associated with the user.But later can be extended to applications etc
        """
        token = g.jwt_oidc_token_info

        # TODO make this check better.may be read from DB or something
        if token.get('sub', None) != user_id:
            return {'message': 'Unauthorised'}, http_status.HTTP_401_UNAUTHORIZED

        try:
            user = UserService.find_by_jwt_token(token)
            if not user:
                response, status = json.dumps([]), http_status.HTTP_200_OK
            else:
                all_settings = UserSettingsService.fetch_user_settings(user.identifier)
                response, status = UserSettingsSchema(many=True).dumps(all_settings), http_status.HTTP_200_OK

        except BusinessException:
            response, status = json.dumps([]), http_status.HTTP_200_OK
        return response, status

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

import json

from flask import request
from flask_restplus import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.exceptions import BusinessException, catch_custom_exception
from auth_api.exceptions.errors import Error
from auth_api.services.keycloak import KeycloakService
from auth_api.tracer import Tracer
from auth_api.utils.util import cors_preflight


API = Namespace('logout', description='Authentication System - Logout User')
KEYCLOAK_SERVICE = KeycloakService()
TRACER = Tracer.get_instance()


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class Logout(Resource):
    """Logout user from keycloak by refresh token."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @catch_custom_exception
    def post():
        """Return a JSON object that includes user detail information."""
        data = request.get_json()
        if not data:
            data = request.values
        try:
            if 'refresh_token' in data:
                response = KEYCLOAK_SERVICE.logout(data.get('refresh_token'))
            else:
                raise BusinessException(Error.INVALID_REFRESH_TOKEN, None)

            return json.dumps(response), http_status.HTTP_204_NO_CONTENT
        except BusinessException as err:
            return json.dumps({'error': '{}'.format(err.code), 'message': '{}'.format(err.error),
                               'detail': '{}'.format(err.detail)}), err.status_code

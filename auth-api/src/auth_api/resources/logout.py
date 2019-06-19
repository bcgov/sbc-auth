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
from flask import jsonify

from flask_restplus import Namespace, Resource
from flask_jwt_oidc import AuthError

from auth_api import status as http_status
from auth_api import tracing as _tracing
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.util import cors_preflight
from auth_api.exceptions import catch_custom_exception
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error


API = Namespace('logout', description='Authentication System - Logout User')
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


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class Logout(Resource):
    """Retrieve user detail information from token and database """

    @staticmethod
    @_tracing.trace()
    @catch_custom_exception
    def post():
        """Return a JSON object that includes user detail information"""
        data = request.get_json()
        if not data:
            data = request.values
        try:
            if 'refresh_token' in data:
                response = KEYCLOAK_SERVICE.logout(data.get('refresh_token'))
            else:
                raise BusinessException(Error.INVALID_REFRESH_TOKEN)

            return response, http_status.HTTP_204_NO_CONTENT
        except BusinessException as err:
            return json.dumps({'error': '{}'.format(err.code), 'message': '{}'.format(err.error),
                               'detail': '{}'.format(err.detail)}), err.status_code

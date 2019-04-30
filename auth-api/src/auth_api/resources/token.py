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
"""Endpoints to get token from Keycloak """

import traceback
from flask import jsonify, request
from flask_restplus import Resource, Namespace
from auth_api.services.keycloak import KeycloakService
from auth_api.services import User
import opentracing
from flask_opentracing import FlaskTracing
from ..utils.trace_tags import TraceTags as tags
from flask import current_app
import os
from jose import jwt
from auth_api.utils.util import cors_preflight


API = Namespace('token', description='Authentication System - Passcode login')
KEYCLOAK_SERVICE = KeycloakService()


tracer = opentracing.tracer
tracing = FlaskTracing(tracer)


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class Token(Resource):
    """Get token from Keycloak by username and password, or refresh token, return token"""
    @staticmethod
    @cors.crossdomain(origin='*')
    @tracing.trace()
    def post():
        """Get token or refresh token, return token"""

        current_span = tracer.active_span
        data = request.get_json()
        if not data:
            data = request.values
        try:
            if data.get('refresh_token'):
                response = KEYCLOAK_SERVICE.refresh_token(data.get('refresh_token'))
            else:
                response = KEYCLOAK_SERVICE.get_token(data.get('username'), data.get('password'))

            return response, 200
        except Exception as err:
            current_span.set_tag(tags.ERROR, 'true')
            tb = traceback.format_exc()
            current_span.log_kv({'event': 'error',
                                 'error.kind': str(type(err)),
                                 'error.message': err.with_traceback(None),
                                 'error.object': tb})
            current_span.set_tag(tags.HTTP_STATUS_CODE, 500)
            return {"error": "{}".format(err)}, 500\

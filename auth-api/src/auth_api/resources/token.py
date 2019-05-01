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

import json

import traceback
import opentracing

from flask import request
from flask_restplus import Resource, Namespace, cors
from flask_opentracing import FlaskTracing

from auth_api.services.keycloak import KeycloakService
from auth_api.utils.util import cors_preflight

from ..utils.trace_tags import TraceTags as tags


API = Namespace('token', description='Authentication System - Passcode login')
KEYCLOAK_SERVICE = KeycloakService()


TRACER = opentracing.tracer
TRACING = FlaskTracing(TRACER)


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class Token(Resource):
    """Get token from Keycloak by username and password, or refresh token, return token"""
    @staticmethod
    @cors.crossdomain(origin='*')
    @TRACING.trace()
    def post():
        """Get token or refresh token, return token"""

        current_span = TRACER.active_span
        data = request.get_json()
        if not data:
            data = request.values
        try:
            if data.get('refresh_token'):
                response = KEYCLOAK_SERVICE.refresh_token(data.get('refresh_token'))
            else:
                response = KEYCLOAK_SERVICE.get_token(data.get('username'), data.get('password'))

            return json.dumps(response), 200
        except Exception as err:
            current_span.set_tag(tags.ERROR, 'true')
            trace_back = traceback.format_exc()
            current_span.log_kv({'event': 'error',
                                 'error.kind': str(type(err)),
                                 'error.message': err.with_traceback(None),
                                 'error.object': trace_back})
            current_span.set_tag(tags.HTTP_STATUS_CODE, 500)
            return json.dumps({"error": "{}".format(err)}), 500\


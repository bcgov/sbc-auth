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

import traceback
import opentracing

from flask import request
from flask_restplus import Resource, Namespace
from flask_opentracing import FlaskTracing

from auth_api.services.keycloak import KeycloakService
from auth_api.utils.util import cors_preflight

from auth_api.utils.trace_tags import TraceTags as tags


API = Namespace('admin/users', description='Keycloak Admin - user')
KEYCLOAK_SERVICE = KeycloakService()

TRACER = opentracing.tracer
TRACING = FlaskTracing(TRACER)


@cors_preflight('GET, POST, DELETE, OPTIONS')
@API.route('', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
class User(Resource):
    """End point resource to manage users."""

    @staticmethod
    @TRACING.trace()
    def post():
        """Add user, return a new/existing user."""

        current_span = TRACER.active_span
        data = request.get_json()
        if not data:
            data = request.values
        try:
            response = KEYCLOAK_SERVICE.add_user(data)

            return response, 201
        except Exception as err:
            current_span.set_tag(tags.ERROR, 'true')
            trace_back = traceback.format_exc()
            current_span.log_kv({'event': 'error',
                                 'error.kind': str(type(err)),
                                 'error.message': err.with_traceback(None),
                                 'error.object': trace_back})
            current_span.set_tag(tags.HTTP_STATUS_CODE, 500)
            return {"error": "{}".format(err)}, 500\


    @staticmethod
    @TRACING.trace()
    def get():
        """Get user by username and return a user"""

        current_span = TRACER.active_span
        data = request.get_json()
        if not data:
            data = request.values
        try:
            user = KEYCLOAK_SERVICE.get_user_by_username(data.get("username"))
            return user, 200
        except Exception as err:
            current_span.set_tag(tags.ERROR, 'true')
            trace_back = traceback.format_exc()
            current_span.log_kv({'event': 'error',
                                 'error.kind': str(type(err)),
                                 'error.message': err.with_traceback(None),
                                 'error.object': trace_back})
            current_span.set_tag(tags.HTTP_STATUS_CODE, 500)
            return {"error": "{}".format(err)}, 500\


    @staticmethod
    @TRACING.trace()
    def delete():
        """Delete user by username"""

        current_span = TRACER.active_span
        data = request.get_json()
        if not data:
            data = request.values
        try:
            response = KEYCLOAK_SERVICE.delete_user_by_username(data.get("username"))
            return response, 204
        except Exception as err:
            current_span.set_tag(tags.ERROR, 'true')
            trace_back = traceback.format_exc()
            current_span.log_kv({'event': 'error',
                                 'error.kind': str(type(err)),
                                 'error.message': err.with_traceback(None),
                                 'error.object': trace_back})
            current_span.set_tag(tags.HTTP_STATUS_CODE, 500)
            return {"error": "{}".format(err)}, 500\


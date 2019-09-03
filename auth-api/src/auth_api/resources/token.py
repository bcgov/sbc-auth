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
"""Endpoints to get token from Keycloak."""

import json

from flask import request
from flask_restplus import Namespace, Resource, cors
from sbc_common_components.tracing.trace_tags import TraceTags

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.services import Entity as EntityService
from auth_api.services.keycloak import KeycloakService
from auth_api.tracer import Tracer
from auth_api.utils.util import cors_preflight


API = Namespace('token', description='Authentication System - Passcode login')
KEYCLOAK_SERVICE = KeycloakService()
TRACER = Tracer.get_instance()


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class Token(Resource):
    """Get token from Keycloak by username and password, or refresh token, return token."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @TRACER.trace()
    def post():
        """Get token or refresh token, return token."""
        data = request.get_json()
        if not data:
            data = request.values
        try:
            if 'refresh_token' in data:
                response = KEYCLOAK_SERVICE.refresh_token(data.get('refresh_token'))
            else:
                response = KEYCLOAK_SERVICE.get_token(data.get('username'), data.get('password'))

            # Check if entity record exists in AUTH, and if not create record
            # TODO: This should be removed once a proper method of syncing entity information is implemented
            entity = EntityService.find_by_business_identifier(data.get('username'))
            if not entity:
                EntityService.create_entity({
                    'businessIdentifier': data.get('username'),
                    'passCode': data.get('password'),
                    'businessNumber': 'ABC123',
                    'name': 'Test Cooperative - {}'.format(data.get('username'))
                })

            current_span = TRACER.tracer.active_span

            with TRACER.tracer.start_active_span('passcode_login', child_of=current_span) as scope:
                scope.span.set_tag(TraceTags.USER, data.get('username'))
                TRACER.inject_tracing_header(response, TRACER.tracer)

            return json.dumps(response), http_status.HTTP_200_OK
        except BusinessException as err:
            return json.dumps({'error': '{}'.format(err.code), 'message': '{}'.format(err.error),
                               'detail': '{}'.format(err.detail)}), err.status_code

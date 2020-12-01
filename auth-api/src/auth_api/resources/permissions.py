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
"""API endpoints for managing a Product resource."""

import json

from flask import request
from flask_restplus import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.services import Permissions as PermissionsService
from auth_api.tracer import Tracer
from auth_api.utils.util import cors_preflight

API = Namespace('permissions', description='Endpoints for permissions management')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET,OPTIONS')
@API.route('/<string:org_status>/<string:membership_type>', methods=['GET', 'OPTIONS'])
class Permissions(Resource):
    """Resource for managing products."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def get(org_status, membership_type):
        """Get a list of all permissions for the membership."""
        try:
            case = request.args.get('case')
            permissions = PermissionsService.get_permissions_for_membership(org_status.upper(), membership_type.upper())
            # TODO Remove this logic once UI part is done.
            #  UI still expects the value as upper .Rather than touching all UI code , changing this.
            if case == 'lower':
                permissions = [x.lower() for x in permissions]
            elif case == 'upper':
                permissions = [x.upper() for x in permissions]

            response, status = json.dumps(permissions), \
                http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

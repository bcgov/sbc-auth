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
"""API endpoints for managing an Org resource."""

from flask import request
from flask_restx import Namespace, Resource, cors

from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.services.org import Org
from auth_api.tracer import Tracer
from auth_api.utils.roles import Role
from auth_api.utils.util import cors_preflight


API = Namespace('BC Online Profiles', description='Endpoints for BC Online Profiles')

TRACER = Tracer.get_instance()


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class BcOnlineProfiles(Resource):
    """Resource for validating BC Online account."""

    @staticmethod
    @_jwt.has_one_of_roles([Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def post():
        """Return BC Online profile details."""
        request_json = request.get_json()

        try:
            bcol_response = Org.get_bcol_details(bcol_credential=request_json)
            response, status = bcol_response.json(), bcol_response.status_code
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

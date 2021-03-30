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
"""API endpoints for managing a Staff Task resource."""

import json
from flask_restplus import Namespace, Resource, cors
from auth_api.tracer import Tracer
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.utils.util import cors_preflight
from auth_api.utils.roles import Role
from auth_api.services import StaffTask as StaffTaskService
from auth_api import status as http_status
from auth_api.exceptions import BusinessException


API = Namespace('stafftasks', description='Endpoints for staff tasks management')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET,POST,OPTIONS')
@API.route('', methods=['GET', 'POST', 'OPTIONS'])
class StaffTasks(Resource):
    """Resource for managing staff tasks."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles(
        [Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def get():
        """fetch staff tasks."""
        try:
            response, status = json.dumps(StaffTaskService.fetch_staff_tasks()), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


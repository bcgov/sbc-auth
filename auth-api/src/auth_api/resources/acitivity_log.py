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
"""API endpoints for managing a Activity resource."""

from flask import request
from flask_restx import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.services import ActivityLog as ActivityLogService
from auth_api.tracer import Tracer
from auth_api.utils.roles import Role
from auth_api.utils.util import cors_preflight


API = Namespace('activity_logs', description='Endpoints for activity management')
TRACER = Tracer.get_instance()


@cors_preflight('GET,OPTIONS')
@API.route('', methods=['GET', 'OPTIONS'])
class ActivityLog(Resource):
    """Resource for fetching Activity Log."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF.value, Role.ACCOUNT_HOLDER.value])
    def get(org_id):
        """Fetch activities."""
        try:
            # Search based on request arguments
            item_name = request.args.get('itemName', None)
            item_type = request.args.get('itemType', None)
            action = request.args.get('action', None)
            page = request.args.get('page', 1)
            limit = request.args.get('limit', 10)

            response, status = ActivityLogService.fetch_activity_logs(org_id,
                                                                      item_name=item_name,
                                                                      item_type=item_type, action=action,
                                                                      page=page, limit=limit), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

        return response, status

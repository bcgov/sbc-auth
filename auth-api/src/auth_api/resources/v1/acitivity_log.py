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

from flask import Blueprint, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.services import ActivityLog as ActivityLogService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import Role


bp = Blueprint('ACTIVITY_LOGS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/orgs/<int:org_id>/activity-logs')
TRACER = Tracer.get_instance()


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@TRACER.trace()
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF.value, Role.ACCOUNT_HOLDER.value])
def get_activities(org_id):
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

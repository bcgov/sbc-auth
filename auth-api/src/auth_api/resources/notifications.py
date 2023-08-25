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
"""API endpoints for managing an Notification resource."""

from flask import Blueprint
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.services import Membership as MembershipService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import Role


bp = Blueprint('NOTIFICATIONS', __name__,
               url_prefix=f'{EndpointEnum.API_V1.value}/users/<string:user_id>/org/<int:org_id>/notifications')
TRACER = Tracer.get_instance()


@bp.route('', methods=['GET', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF.value, Role.PUBLIC_USER.value])
def get_notifications(user_id, org_id):  # pylint:disable=unused-argument
    """Find the count of notification remaining.If any details invalid, it returns zero."""
    try:
        # todo use the user_id instead of jwt
        pending_count = MembershipService.get_pending_member_count_for_org(org_id)
        response, status = {'count': pending_count}, http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status

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
"""Endpoints to reset test data from database."""

from flask import Blueprint
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.services import ResetTestData as ResetService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import Role


bp = Blueprint('RESET', __name__, url_prefix=f'{EndpointEnum.TEST_API.value}/reset')
TRACER = Tracer.get_instance()


@bp.route('', methods=['POST'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.has_one_of_roles([Role.TESTER.value])
def post_reset():
    """Cleanup test data by the provided token."""
    try:
        ResetService.reset()
        response, status = '', http_status.HTTP_204_NO_CONTENT
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status

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
"""API endpoints for managing EFT Accounts."""
from flask import Blueprint, g, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.models.dataclass import EftAccountsSearch
from auth_api.services import Org as OrgService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import Role  # noqa: I005


bp = Blueprint('EFT_ACCOUNTS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/eft-accounts')
TRACER = Tracer.get_instance()


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET', 'POST'])
@TRACER.trace()
@_jwt.has_one_of_roles(
    [Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value])
def search_eft_accounts():
    """Search orgs."""
    eft_accounts_search = EftAccountsSearch(
        request.args.get('state', None),
        int(request.args.get('page', 1)),
        int(request.args.get('limit', 10))
    )
    try:
        token = g.jwt_oidc_token_info
        response, status = OrgService.get_eft_orgs(eft_accounts_search), http_status.HTTP_200_OK

        roles = token.get('realm_access').get('roles')
        allowed_roles = [Role.STAFF.value, Role.SYSTEM.value, Role.ACCOUNT_IDENTITY]
        if Role.PUBLIC_USER.value in roles and not set(roles).intersection(set(allowed_roles)):
            if response and response.get('orgs'):
                status = http_status.HTTP_200_OK
            else:
                status = http_status.HTTP_204_NO_CONTENT
            response = {}  # Do not return any results if searching by name

    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status

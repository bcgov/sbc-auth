# Copyright © 2024 Province of British Columbia
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
"""API endpoints for searching organizations for a simplified data set."""
from flask import Blueprint, current_app, jsonify, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.models.dataclass import SimpleOrgSearch
from auth_api.services import SimpleOrg as SimpleOrgService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.enums import OrgStatus
from auth_api.utils.roles import Role

bp = Blueprint('SIMPLE_ORG', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/simple-orgs')
TRACER = Tracer.get_instance()


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET'])
@TRACER.trace()
@_jwt.has_one_of_roles(
    [Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value])
def search_simple_orgs():
    """Return simplified organization information."""
    current_app.logger.info('<search_simple_orgs')

    org_id = request.args.get('id', None)
    page: int = int(request.args.get('page', '1'))
    limit: int = int(request.args.get('limit', '10'))
    name = request.args.get('name', None)
    branch_name = request.args.get('branchName', None)
    search_text = request.args.get('searchText', None)
    status = request.args.get('status', OrgStatus.ACTIVE.value)

    response, status = SimpleOrgService.search(SimpleOrgSearch(
        id=org_id,
        name=name,
        branch_name=branch_name,
        search_text=search_text,
        status=status,
        page=page,
        limit=limit)), http_status.HTTP_200_OK

    current_app.logger.info('>search_simple_orgs')
    return jsonify(response), status

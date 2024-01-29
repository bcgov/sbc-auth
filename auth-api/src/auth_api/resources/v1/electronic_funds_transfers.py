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
"""API endpoints for managing Electronic Funds Transfers resource."""
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.services import ElectronicFundsTransfersService
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import Role  # noqa: I005

bp = Blueprint('ELECTRONIC_FUNDS_TRANSFERS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/electronic-funds-transfers')


@bp.route('/short-names/unlinked', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET'])
@_jwt.has_one_of_roles(
    [Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
def get_unlinked_electronic_funds_transfers_short_names():
    """Return all unlinked short names for electronic funds transfers."""
    try:
        include_all=True
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 10))
        electronic_funds_transfers_short_names = ElectronicFundsTransfersService \
            .get_electronic_funds_transfers_short_names(include_all, page, limit)
        if electronic_funds_transfers_short_names is not None:
            response, status = jsonify(electronic_funds_transfers_short_names), http_status.HTTP_200_OK
        else:
            response, status = jsonify({'message': f'No electronic funds transfers short names found.'}), \
                http_status.HTTP_404_NOT_FOUND
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status

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
"""API endpoints for managing an Invitation resource."""
from flask import Blueprint, jsonify
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.services import Codes as CodeService
from auth_api.utils.endpoints_enums import EndpointEnum

bp = Blueprint('CODES', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/codes')


@bp.route('/<string:code_type>', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET'])
def get_codes(code_type):
    """Return the codes by giving name."""
    try:
        codes = CodeService.fetch_codes(code_type=code_type)
        if codes is not None:
            response, status = jsonify(codes), http_status.HTTP_200_OK
        else:
            response, status = jsonify({'message': f'The code type ({code_type}) could not be found.'}), \
                http_status.HTTP_404_NOT_FOUND
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status

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
"""API endpoints for managing a Product resource."""

import json

from flask import Blueprint
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.services import Product as ProductService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum


bp = Blueprint('PRODUCTS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/products')
TRACER = Tracer.get_instance()


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET'])
@TRACER.trace()
def get_products():
    """Get a list of all products."""
    try:
        response, status = json.dumps(ProductService.get_products()), http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status

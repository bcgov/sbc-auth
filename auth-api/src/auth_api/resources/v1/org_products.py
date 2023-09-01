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
"""API endpoints for managing an Org resource."""
import json

from flask import Blueprint, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.schemas import utils as schema_utils
from auth_api.services import Product as ProductService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import Role


bp = Blueprint('ORG_PRODUCTS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/orgs/<int:org_id>/products')
TRACER = Tracer.get_instance()


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET', 'POST'])
@TRACER.trace()
@_jwt.has_one_of_roles([Role.PUBLIC_USER.value, Role.STAFF_VIEW_ACCOUNTS.value])
def get_org_product_subscriptions(org_id):
    """GET a new product subscription to the org using the request body."""
    try:
        include_hidden = request.args.get('include_hidden', None) == 'true'  # used by NDS
        response, status = json.dumps(ProductService.get_all_product_subscription(org_id=org_id,
                                                                                  include_hidden=include_hidden)
                                      ), http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('', methods=['POST'])
@cross_origin(origins='*')
@TRACER.trace()
@_jwt.has_one_of_roles([Role.STAFF_CREATE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def post_org_product_subscription(org_id):
    """Post a new product subscription to the org using the request body."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, 'org_product_subscription')
    if not valid_format:
        return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

    try:
        subscriptions = ProductService.create_product_subscription(org_id, request_json)
        ProductService.update_org_product_keycloak_groups(org_id)
        response, status = {'subscriptions': subscriptions}, http_status.HTTP_201_CREATED
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status

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
from http import HTTPStatus

from flask import Blueprint, g, request
from flask_cors import cross_origin

from auth_api.exceptions import BusinessException
from auth_api.schemas import utils as schema_utils
from auth_api.services import Product as ProductService
from auth_api.utils.auth import jwt as _jwt
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import Role

bp = Blueprint("ORG_PRODUCTS", __name__, url_prefix=f"{EndpointEnum.API_V1.value}/orgs/<string:org_id>/products")


@bp.route("", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET", "PATCH", "POST"])
@_jwt.has_one_of_roles([Role.PUBLIC_USER.value, Role.STAFF_VIEW_ACCOUNTS.value])
def get_org_product_subscriptions(org_id):
    """GET a new product subscription to the org using the request body."""

    if not org_id or org_id == "None" or not org_id.isdigit() or int(org_id) < 0:
        return {"message": "The organization ID is in an incorrect format."}, HTTPStatus.BAD_REQUEST

    try:
        include_hidden = request.args.get("include_hidden", None) == "true"  # used by NDS
        response, status = (
            json.dumps(ProductService.get_all_product_subscription(org_id=int(org_id), include_hidden=include_hidden)),
            HTTPStatus.OK,
        )
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("", methods=["POST"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.STAFF_CREATE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def post_org_product_subscription(org_id):
    """Post a new product subscription to the org using the request body."""

    if not org_id or org_id == "None" or not org_id.isdigit() or int(org_id) < 0:
        return {"message": "The organization ID is in an incorrect format."}, HTTPStatus.BAD_REQUEST

    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, "org_product_subscription")
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST

    try:
        roles = g.jwt_oidc_token_info.get('realm_access').get('roles')
        subscriptions = ProductService.create_product_subscription(int(org_id), request_json,
                                                                   skip_auth=Role.SYSTEM.value in roles,
                                                                   auto_approve=Role.SYSTEM.value in roles)
        ProductService.update_org_product_keycloak_groups(int(org_id))
        response, status = {'subscriptions': subscriptions}, HTTPStatus.CREATED
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("", methods=["PATCH"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.PUBLIC_USER.value])
def patch_org_product_subscription(org_id):
    """Patch existing product subscription to resubmit it for review."""

    if not org_id or org_id == "None" or not org_id.isdigit() or int(org_id) < 0:
        return {"message": "The organization ID is in an incorrect format."}, HTTPStatus.BAD_REQUEST

    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, "org_product_subscription")
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST

    try:
        subscriptions = ProductService.resubmit_product_subscription(int(org_id), request_json)
        response, status = {"subscriptions": subscriptions}, HTTPStatus.OK
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status

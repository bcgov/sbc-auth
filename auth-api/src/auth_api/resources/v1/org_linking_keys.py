# Copyright © 2026 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""API endpoints for managing linking keys for an org."""

from http import HTTPStatus

from flask import Blueprint, request
from flask_cors import cross_origin

from auth_api.schemas import AccountLinkingKeySchema
from auth_api.schemas import utils as schema_utils
from auth_api.services import Org as OrgService
from auth_api.services.account_linking_key import AccountLinkingKey as AccountLinkingKeyService
from auth_api.services.flags import flags
from auth_api.utils.auth import jwt as _jwt
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import ADMIN, COORDINATOR, Role

bp = Blueprint("LINKING_KEYS", __name__, url_prefix=f"{EndpointEnum.API_V1.value}/orgs/<int:org_id>/linking-keys")

_OWNER_ROLES = (COORDINATOR, ADMIN)


@bp.before_request
def _check_feature_enabled():
    if flags.is_on("disable-account-linking", default=False):
        return {"message": "Account linking is not available."}, HTTPStatus.NOT_IMPLEMENTED


@bp.route("", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET", "POST"])
@_jwt.has_one_of_roles([Role.ACCOUNT_HOLDER.value, Role.STAFF_MANAGE_ACCOUNTS.value])
def get_linking_keys(org_id):
    """List all active linking keys for the org (key values are never returned)."""
    org = OrgService.find_by_org_id(org_id, allowed_roles=_OWNER_ROLES)
    if org is None:
        return {"message": "The requested organization could not be found."}, HTTPStatus.NOT_FOUND
    records = AccountLinkingKeyService.get_all(org_id)
    return {"linkingKeys": AccountLinkingKeySchema(exclude=["linking_key"], many=True).dump(records)}, HTTPStatus.OK


@bp.route("", methods=["POST"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.ACCOUNT_HOLDER.value, Role.STAFF_MANAGE_ACCOUNTS.value])
def post_linking_key(org_id):
    """Generate a new linking key for the org. Returns the key value once on creation."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, "linking_key")
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST
    org = OrgService.find_by_org_id(org_id, allowed_roles=_OWNER_ROLES)
    if org is None:
        return {"message": "The requested organization could not be found."}, HTTPStatus.NOT_FOUND
    record = AccountLinkingKeyService.generate(org_id, request_json["vendorAccountId"])
    return AccountLinkingKeySchema().dump(record), HTTPStatus.CREATED


@bp.route("/<int:key_id>", methods=["DELETE"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.ACCOUNT_HOLDER.value, Role.STAFF_MANAGE_ACCOUNTS.value])
def delete_linking_key(org_id, key_id):
    """Revoke a specific linking key by ID (soft delete)."""
    org = OrgService.find_by_org_id(org_id, allowed_roles=_OWNER_ROLES)
    if org is None:
        return {"message": "The requested organization could not be found."}, HTTPStatus.NOT_FOUND
    found = AccountLinkingKeyService.revoke(key_id, org_id)
    if not found:
        return {}, HTTPStatus.NOT_FOUND
    return {}, HTTPStatus.OK

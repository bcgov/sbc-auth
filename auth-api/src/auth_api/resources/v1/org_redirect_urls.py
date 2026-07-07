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
"""API endpoints for managing redirect URLs for a vendor org."""

from http import HTTPStatus

from flask import Blueprint, request
from flask_cors import cross_origin

from auth_api.schemas import OrgRedirectUrlSchema
from auth_api.schemas import utils as schema_utils
from auth_api.services import Org as OrgService
from auth_api.services.org_redirect_url import OrgRedirectUrl as OrgRedirectUrlService
from auth_api.utils.auth import jwt as _jwt
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import ADMIN, COORDINATOR, Role

bp = Blueprint("REDIRECT_URLS", __name__, url_prefix=f"{EndpointEnum.API_V1.value}/orgs/<int:org_id>/redirect-urls")

_OWNER_ROLES = (COORDINATOR, ADMIN)


@bp.route("", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET", "POST"])
@_jwt.has_one_of_roles([Role.ACCOUNT_HOLDER.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.STAFF.value])
def get_redirect_urls(org_id):
    """List all redirect URLs for the org."""
    org = OrgService.find_by_org_id(org_id)
    if org is None:
        return {"message": "The requested organization could not be found."}, HTTPStatus.NOT_FOUND
    records = OrgRedirectUrlService.get_all(org_id)
    return {"redirectUrls": OrgRedirectUrlSchema(many=True).dump(records)}, HTTPStatus.OK


@bp.route("", methods=["POST"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.ACCOUNT_HOLDER.value, Role.STAFF_MANAGE_ACCOUNTS.value])
def post_redirect_url(org_id):
    """Add a new redirect URL for the org."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, "org_redirect_url")
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST
    org = OrgService.find_by_org_id(org_id, allowed_roles=_OWNER_ROLES)
    if org is None:
        return {"message": "The requested organization could not be found."}, HTTPStatus.NOT_FOUND
    record, error = OrgRedirectUrlService.create(org_id, request_json["redirectUrl"])
    if error:
        return {"message": error}, HTTPStatus.CONFLICT if "already" in error else HTTPStatus.BAD_REQUEST
    return OrgRedirectUrlSchema().dump(record), HTTPStatus.CREATED


@bp.route("/<int:url_id>", methods=["PATCH"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.ACCOUNT_HOLDER.value, Role.STAFF_MANAGE_ACCOUNTS.value])
def patch_redirect_url(org_id, url_id):
    """Update an existing redirect URL."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, "org_redirect_url")
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST
    org = OrgService.find_by_org_id(org_id, allowed_roles=_OWNER_ROLES)
    if org is None:
        return {"message": "The requested organization could not be found."}, HTTPStatus.NOT_FOUND
    record, error = OrgRedirectUrlService.update(url_id, org_id, request_json["redirectUrl"])
    if error == "not_found":
        return {}, HTTPStatus.NOT_FOUND
    if error:
        return {"message": error}, HTTPStatus.CONFLICT if "already" in error else HTTPStatus.BAD_REQUEST
    return OrgRedirectUrlSchema().dump(record), HTTPStatus.OK


@bp.route("/<int:url_id>", methods=["DELETE"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.ACCOUNT_HOLDER.value, Role.STAFF_MANAGE_ACCOUNTS.value])
def delete_redirect_url(org_id, url_id):
    """Delete a redirect URL."""
    org = OrgService.find_by_org_id(org_id, allowed_roles=_OWNER_ROLES)
    if org is None:
        return {"message": "The requested organization could not be found."}, HTTPStatus.NOT_FOUND
    found = OrgRedirectUrlService.delete(url_id, org_id)
    if not found:
        return {}, HTTPStatus.NOT_FOUND
    return {}, HTTPStatus.OK

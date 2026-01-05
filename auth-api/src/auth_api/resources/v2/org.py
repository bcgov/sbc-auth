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
"""API endpoints for managing an Org resource - V2."""

from http import HTTPStatus

from flask import Blueprint, request
from flask_cors import cross_origin

from auth_api.exceptions import BusinessException
from auth_api.schemas import utils as schema_utils
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService
from auth_api.utils.auth import jwt as _jwt
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.role_validator import validate_roles
from auth_api.utils.roles import Role

bp = Blueprint("ORGS_V2", __name__, url_prefix=f"{EndpointEnum.API_V2.value}/orgs")


@bp.route("", methods=["POST"])
@cross_origin(origins="*")
@validate_roles(
    allowed_roles=[Role.PUBLIC_USER.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.SYSTEM.value],
    not_allowed_roles=[Role.ANONYMOUS_USER.value],
)
@_jwt.has_one_of_roles([Role.PUBLIC_USER.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.SYSTEM.value])
def post_organization():
    """Post a new org with contact using the request body.

    Creates an organization and then adds a contact if provided.
    Validates both org and contact schemas before processing.
    """
    request_json = request.get_json()
    if not request_json:
        return {"message": "Request body cannot be empty"}, HTTPStatus.BAD_REQUEST

    org_info = request_json.copy()
    contact_info = org_info.pop("contact", None)

    if contact_info:
        org_info.pop("mailingAddress", None)

    valid_format, errors = schema_utils.validate(org_info, "org")
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST

    if contact_info:
        valid_contact_format, contact_errors = schema_utils.validate(contact_info, "contact")
        if not valid_contact_format:
            return {"message": schema_utils.serialize(contact_errors)}, HTTPStatus.BAD_REQUEST

    try:
        user = UserService.find_by_jwt_token()
        if user is None:
            response, status = {"message": "Not authorized to perform this action"}, HTTPStatus.UNAUTHORIZED
            return response, status

        org = OrgService.create_org(org_info, user.identifier)
        org_dict = org.as_dict()
        org_id = org_dict.get("id")

        if contact_info and org_id:
            contact = OrgService.add_contact(org_id, contact_info)
            org_dict["contact"] = contact.as_dict()

        response, status = org_dict, HTTPStatus.CREATED
    except BusinessException as exception:
        response, status = (
            {
                "code": exception.code,
                "message": exception.message,
                "detail": exception.detail,
            },
            exception.status_code,
        )
    return response, status

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
import asyncio
from http import HTTPStatus

import orjson
from flask import Blueprint, current_app, g, jsonify, request
from flask_cors import cross_origin

from auth_api.exceptions import BusinessException, ServiceUnavailableException
from auth_api.exceptions.errors import Error
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Org as OrgModel
from auth_api.models.dataclass import Affiliation as AffiliationData
from auth_api.models.dataclass import AffiliationSearchDetails, DeleteAffiliationRequest, SimpleOrgSearch
from auth_api.models.org import OrgSearch  # noqa: I005; Not sure why isort doesn't like this
from auth_api.schemas import InvitationSchema, MembershipSchema
from auth_api.schemas import utils as schema_utils
from auth_api.services import Affidavit as AffidavitService
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import Invitation as InvitationService
from auth_api.services import Membership as MembershipService
from auth_api.services import Org as OrgService
from auth_api.services import SimpleOrg as SimpleOrgService
from auth_api.services import User as UserService
from auth_api.services.authorization import Authorization as AuthorizationService
from auth_api.services.entity_mapping import EntityMappingService
from auth_api.services.flags import flags
from auth_api.utils.auth import jwt as _jwt
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.enums import AccessType, NotificationType, OrgStatus, OrgType, PatchActions, Status
from auth_api.utils.role_validator import validate_roles
from auth_api.utils.roles import (  # noqa: I005
    AFFILIATION_ALLOWED_ROLES,
    ALL_ALLOWED_ROLES,
    CLIENT_ADMIN_ROLES,
    STAFF,
    USER,
    Role,
)
from auth_api.utils.util import extract_numbers, string_to_bool

bp = Blueprint("ORGS", __name__, url_prefix=f"{EndpointEnum.API_V1.value}/orgs")


@bp.route("", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET", "POST"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
def search_organizations():
    """Search orgs."""
    org_search = OrgSearch(
        request.args.get("name", None),
        request.args.get("branchName", None),
        request.args.get("affiliation", None),
        request.args.getlist("status", None),
        request.args.getlist("accessType", None),
        request.args.get("bcolAccountId", None),
        extract_numbers(request.args.get("id", None)),
        request.args.get("decisionMadeBy", None),
        request.args.get("orgType", None),
        string_to_bool(request.args.get("includeMembers", "False")),
        request.args.get("members", None),
        int(request.args.get("page", 1)),
        int(request.args.get("limit", 10)),
    )
    validate_name = request.args.get("validateName", "False")
    try:
        token = g.jwt_oidc_token_info
        if validate_name.upper() == "TRUE":
            response, status = (
                OrgService.find_by_org_name(org_name=org_search.name, branch_name=org_search.branch_name),
                HTTPStatus.OK,
            )
        else:
            response, status = OrgService.search_orgs(org_search), HTTPStatus.OK

        roles = token.get("realm_access").get("roles")
        # public user can only get status of orgs in search, unless they have special roles.
        allowed_roles = [Role.STAFF.value, Role.SYSTEM.value, Role.ACCOUNT_IDENTITY, Role.STAFF_VIEW_ACCOUNTS.value]
        if Role.PUBLIC_USER.value in roles and not set(roles).intersection(set(allowed_roles)):
            if response and response.get("orgs"):
                status = HTTPStatus.OK
            else:
                status = HTTPStatus.NO_CONTENT
            response = {}  # Do not return any results if searching by name

    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("/simple", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET"])
@validate_roles(allowed_roles=[Role.MANAGE_EFT.value, Role.SYSTEM.value])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.MANAGE_EFT.value])
def search_simple_orgs():
    """Return simplified organization information."""
    current_app.logger.info("<search_simple_orgs")

    org_id = request.args.get("id", None)
    page: int = int(request.args.get("page", "1"))
    limit: int = int(request.args.get("limit", "10"))
    name = request.args.get("name", None)
    branch_name = request.args.get("branchName", None)
    search_text = request.args.get("searchText", None)
    statuses = request.args.getlist("statuses") or [OrgStatus.ACTIVE.value]
    exclude_statuses = request.args.get("excludeStatuses", False)

    response, status = (
        SimpleOrgService.search(
            SimpleOrgSearch(
                id=org_id,
                name=name,
                branch_name=branch_name,
                search_text=search_text,
                statuses=statuses,
                exclude_statuses=exclude_statuses,
                page=page,
                limit=limit,
            )
        ),
        HTTPStatus.OK,
    )

    current_app.logger.info(">search_simple_orgs")
    return jsonify(response), status


@bp.route("", methods=["POST"])
@cross_origin(origins="*")
@validate_roles(
    allowed_roles=[Role.PUBLIC_USER.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.SYSTEM.value],
    not_allowed_roles=[Role.ANONYMOUS_USER.value],
)
@_jwt.has_one_of_roles([Role.PUBLIC_USER.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.SYSTEM.value])
def post_organization():
    """Post a new org using the request body.

    If the org already exists, update the attributes.
    """
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, "org")
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST
    try:
        user = UserService.find_by_jwt_token()
        if user is None:
            response, status = {"message": "Not authorized to perform this action"}, HTTPStatus.UNAUTHORIZED
            return response, status
        response, status = OrgService.create_org(request_json, user.identifier).as_dict(), HTTPStatus.CREATED
    except BusinessException as exception:
        response, status = {
            "code": exception.code,
            "message": exception.message,
            "detail": exception.detail,
        }, exception.status_code
    return response, status


@bp.route("/<int:org_id>", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET", "PUT", "PATCH", "DELETE"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
def get_organization(org_id):
    """Get the org specified by the provided id."""
    org = OrgService.find_by_org_id(org_id, allowed_roles=ALL_ALLOWED_ROLES)
    if org is None:
        response, status = {"message": "The requested organization could not be found."}, HTTPStatus.NOT_FOUND
    else:
        response, status = org.as_dict(), HTTPStatus.OK
    return response, status


@bp.route("/<int:org_id>", methods=["PUT"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles(
    [Role.SYSTEM.value, Role.PUBLIC_USER.value, Role.GOV_ACCOUNT_USER.value, Role.STAFF_MANAGE_ACCOUNTS.value]
)
def put_organization(org_id):
    """Update the org specified by the provided id with the request body."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, "org")
    token_info = g.jwt_oidc_token_info
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST
    try:
        org = OrgService.find_by_org_id(org_id, allowed_roles=(*CLIENT_ADMIN_ROLES, STAFF))
        if (
            org
            and org.as_dict().get("accessType", None) == AccessType.ANONYMOUS.value
            and Role.STAFF_CREATE_ACCOUNTS.value not in token_info.get("realm_access").get("roles")
        ):
            return {"message": "The organisation can only be updated by a staff admin."}, HTTPStatus.UNAUTHORIZED
        if org:
            response, status = org.update_org(org_info=request_json).as_dict(), HTTPStatus.OK
        else:
            response, status = {"message": "The requested organization could not be found."}, HTTPStatus.NOT_FOUND
    except BusinessException as exception:
        response, status = {
            "code": exception.code,
            "message": exception.message,
            "detail": exception.detail,
        }, exception.status_code
    return response, status


@bp.route("/<int:org_id>", methods=["DELETE"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def delete_organization(org_id):
    """Inactivates the org if it has no active members or affiliations."""
    try:
        OrgService.delete_org(org_id)
        response, status = "", HTTPStatus.NO_CONTENT
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("/<int:org_id>", methods=["PATCH"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.STAFF_MANAGE_ACCOUNTS.value, Role.SYSTEM.value])
def patch_organization(org_id):
    """Patch an account."""
    request_json = request.get_json()
    try:
        org = OrgService(OrgModel.find_by_org_id(org_id))
        if org:
            # set default patch action to updating status action
            action = request_json.get("action", PatchActions.UPDATE_STATUS.value)
            response, status = org.patch_org(action, request_json), HTTPStatus.OK
        else:
            response, status = {"message": "The requested organization could not be found."}, HTTPStatus.NOT_FOUND

    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code

    return response, status


@bp.route("/<int:org_id>/login-options", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET", "POST", "PUT"])
@_jwt.requires_auth
def get_org_login_options(org_id):
    """Retrieve the set of payment settings associated with the specified org."""
    try:
        login_options = OrgService.get_login_options_for_org(org_id, allowed_roles=ALL_ALLOWED_ROLES)
        response, status = (
            jsonify({"loginOption": login_options.login_source if login_options else None}),
            HTTPStatus.OK,
        )
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("/<int:org_id>/login-options", methods=["POST"])
@cross_origin(origins="*")
@_jwt.requires_auth
def post_org_login_options(org_id):
    """Create a new login type for the specified org."""
    request_json = request.get_json()
    login_option_val = request_json.get("loginOption")
    try:
        login_option = OrgService.add_login_option(org_id, login_option_val)
        response, status = jsonify({"login_option": login_option.login_source}), HTTPStatus.CREATED
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("/<int:org_id>/login-options", methods=["PUT"])
@cross_origin(origins="*")
@_jwt.requires_auth
def put_org_login_optjons(org_id):
    """Update a new login type for the specified org."""
    request_json = request.get_json()
    login_option_val = request_json.get("loginOption")
    try:
        login_option = OrgService.update_login_option(org_id, login_option_val)
        response, status = jsonify({"login_option": login_option.login_source}), HTTPStatus.CREATED
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("/<int:org_id>/contacts", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET", "POST", "PUT", "DELETE"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
def get(org_id):
    """Retrieve the set of contacts associated with the specified org."""
    try:
        response, status = OrgService.get_contacts(org_id), HTTPStatus.OK
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("/<int:org_id>/contacts", methods=["POST"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.PUBLIC_USER.value])
def post_organization_contact(org_id):
    """Create a new contact for the specified org."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, "contact")
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST

    try:
        response, status = OrgService.add_contact(org_id, request_json).as_dict(), HTTPStatus.CREATED
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("/<int:org_id>/contacts", methods=["PUT"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.PUBLIC_USER.value])
def put_organization_contact(org_id):
    """Update an existing contact for the specified org."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, "contact")
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST
    try:
        response, status = OrgService.update_contact(org_id, request_json).as_dict(), HTTPStatus.OK
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("/<int:org_id>/contacts", methods=["DELETE"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.PUBLIC_USER.value])
def delete_organzization_contact(org_id):
    """Delete the contact info for the specified org."""
    try:
        response, status = OrgService.delete_contact(org_id).as_dict(), HTTPStatus.OK
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("/<int:org_id>/affiliations/search", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["POST", "GET"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_BUSINESS.value, Role.PUBLIC_USER.value])
def get_organization_affiliations_search(org_id):
    """Get all affiliated entities for the given org, this works with pagination."""
    try:
        response, status = affiliation_search(org_id, use_entity_mapping=True)
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    except ServiceUnavailableException as exception:
        response, status = {"message": exception.error}, exception.status_code
    return response, status


@bp.route("/<int:org_id>/affiliations", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["POST", "GET"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_BUSINESS.value, Role.PUBLIC_USER.value])
def get_organization_affiliations(org_id):
    """Get all affiliated entities for the given org."""
    try:
        if (request.args.get("new", "false")).lower() != "true":
            return (
                jsonify({"entities": AffiliationService.find_visible_affiliations_by_org_id(org_id)}),
                HTTPStatus.OK,
            )
        # Remove below after UI is pointing at new route.
        response, status = affiliation_search(org_id)
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    except ServiceUnavailableException as exception:
        response, status = {"message": exception.error}, exception.status_code

    return response, status


def affiliation_search(org_id, use_entity_mapping=False):
    """Get all affiliated entities for the given org by calling into Names and LEAR."""
    org = OrgService.find_by_org_id(org_id, allowed_roles=AFFILIATION_ALLOWED_ROLES)
    if org is None:
        raise BusinessException(Error.DATA_NOT_FOUND, None)
    search_details = AffiliationSearchDetails.from_request_args(request)
    if use_entity_mapping:
        remove_stale_drafts = False
        affiliation_bases, has_more = EntityMappingService.populate_affiliation_base(org_id, search_details)
        affiliations_details_list, has_more_search = asyncio.run(
            AffiliationService.get_affiliation_details(affiliation_bases, search_details, org_id, remove_stale_drafts)
        )
        # Added Pagination after fetching filtered details from LEAR and Names otherwise searches only on page 1.
        if any([search_details.identifier, search_details.status, search_details.name, search_details.type]):
            has_more = has_more_search

        response = {
            "entities": affiliations_details_list,
            "totalResults": len(affiliations_details_list),
            "hasMore": has_more,
        }
    else:
        remove_stale_drafts = True
        affiliations = AffiliationModel.find_affiliations_by_org_id(org_id)
        affiliation_bases = AffiliationService.affiliation_to_affiliation_base(affiliations)
        affiliations_details_list, _ = asyncio.run(
            AffiliationService.get_affiliation_details(affiliation_bases, search_details, org_id, remove_stale_drafts)
        )
        response = {"entities": affiliations_details_list, "totalResults": len(affiliations_details_list)}
    # Use orjson serializer here, it's quite a bit faster.
    response, status = (
        current_app.response_class(
            response=orjson.dumps(response),  # pylint: disable=maybe-no-member
            status=200,
            mimetype="application/json",
        ),
        HTTPStatus.OK,
    )
    return response, status


@bp.route("/<int:org_id>/affiliations", methods=["POST"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_BUSINESS.value, Role.PUBLIC_USER.value])
def post_organization_affiliation(org_id):
    """Post a new Affiliation for an org using the request body."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, "affiliation")
    is_new_business = request.args.get("newBusiness", "false").lower() == "true"
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST

    business_identifier = request_json.get("businessIdentifier")
    if not any(character.isdigit() for character in business_identifier):
        return {"message": "Business identifier requires at least 1 digit."}, HTTPStatus.BAD_REQUEST
    try:
        if is_new_business:
            affiliation_data = AffiliationData(
                org_id=org_id,
                business_identifier=business_identifier,
                email=request_json.get("email"),
                phone=request_json.get("phone"),
                certified_by_name=request_json.get("certifiedByName"),
            )
            response, status = (
                AffiliationService.create_new_business_affiliation(affiliation_data).as_dict(),
                HTTPStatus.CREATED,
            )
        else:
            response, status = (
                AffiliationService.create_affiliation(
                    org_id,
                    business_identifier,
                    request_json.get("passCode"),
                    request_json.get("certifiedByName"),
                    skip_membership_check=_jwt.has_one_of_roles([Role.SKIP_AFFILIATION_AUTH.value]),
                ).as_dict(),
                HTTPStatus.CREATED,
            )
        entity_details = request_json.get("entityDetails", None)
        if entity_details:
            if flags.is_on("enable-entity-mapping", default=False) is True:
                EntityMappingService.from_entity_details(entity_details)
            AffiliationService.fix_stale_affiliations(org_id, entity_details)
        # Auth-queue handles the row creation for new business (NR only), this handles passcode missing info
        elif is_new_business is False:
            if flags.is_on("enable-entity-mapping", default=False) is True:
                EntityMappingService.populate_entity_mapping_for_identifier(business_identifier)
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code

    return response, status


@bp.route("/affiliation/<string:business_identifier>", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
def get_org_details_by_affiliation(business_identifier):
    """Search non staff orgs by BusinessIdentifier and return org Name, branch Name and UUID."""
    excluded_org_types = [OrgType.STAFF.value, OrgType.SBC_STAFF.value]
    try:
        data = OrgService.search_orgs_by_affiliation(business_identifier, excluded_org_types)

        org_details = [{"name": org.name, "uuid": org.uuid, "branchName": org.branch_name} for org in data["orgs"]]
        response, status = {"orgs_details": org_details}, HTTPStatus.OK

    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("/<int:org_id>/affiliations/<string:business_identifier>", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET", "DELETE"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_BUSINESS.value, Role.PUBLIC_USER.value])
def get_org_affiliation_by_business_identifier(org_id, business_identifier):
    """Get the affiliation by org id and business identifier with authorized user."""
    # Note this is used by LEAR - which passes in the user's token to query for an affiliation for an NR.
    try:
        if AuthorizationService.get_user_authorizations_for_entity(business_identifier):
            # get affiliation
            response, status = (
                AffiliationService.find_affiliation(org_id, business_identifier),
                HTTPStatus.OK,
            )
        else:
            response, status = {"message": "Not authorized to perform this action"}, HTTPStatus.UNAUTHORIZED

    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    except ServiceUnavailableException as exception:
        response, status = {"message": exception.error}, exception.status_code
    return response, status


@bp.route("/<int:org_id>/affiliations/<string:business_identifier>", methods=["DELETE"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_BUSINESS.value, Role.PUBLIC_USER.value])
def delete_org_affiliation_by_business_identifier(org_id, business_identifier):
    """Delete an affiliation between an org and an entity."""
    request_json = request.get_json(silent=True) or {}
    try:
        delete_affiliation_request = DeleteAffiliationRequest(
            org_id=org_id,
            business_identifier=business_identifier,
            email_addresses=request_json.get("passcodeResetEmail"),
            reset_passcode=request_json.get("resetPasscode", False),
            log_delete_draft=request_json.get("logDeleteDraft", False),
        )
        AffiliationService.delete_affiliation(delete_affiliation_request)
        response, status = {}, HTTPStatus.OK

    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code

    return response, status


@bp.route("/<int:org_id>/members", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
def get_organization_members(org_id):
    """Retrieve the set of members for the given org."""
    try:

        status = request.args.get("status").upper() if request.args.get("status") else None
        roles = request.args.get("roles").upper().split(",") if request.args.get("roles") else None

        members = MembershipService.get_members_for_org(org_id, status=status, membership_roles=roles)
        if members:
            response, status = {"members": MembershipSchema(exclude=["org"]).dump(members, many=True)}, HTTPStatus.OK
        else:
            response, status = {}, HTTPStatus.OK

    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code

    return response, status


@bp.route("/<int:org_id>/members/<int:membership_id>", methods=["PATCH", "OPTIONS"])
@cross_origin(origins="*", methods=["PATCH", "DELETE"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def patch_organization_member(org_id, membership_id):  # pylint:disable=unused-argument
    """Update a membership record with new member role."""
    role = request.get_json().get("role")
    membership_status = request.get_json().get("status")
    notify_user = request.get_json().get("notifyUser")
    updated_fields_dict = {}
    origin = request.environ.get("HTTP_ORIGIN", "localhost")
    try:
        if role is not None:
            updated_role = MembershipService.get_membership_type_by_code(role)
            updated_fields_dict["membership_type"] = updated_role
        if membership_status is not None:
            updated_fields_dict["membership_status"] = MembershipService.get_membership_status_by_code(
                membership_status
            )

        membership = MembershipService.find_membership_by_id(membership_id)

        is_own_membership = (
            membership.as_dict()["user"]["username"] == UserService.find_by_jwt_token().as_dict()["username"]
        )
        if not membership:
            response, status = {"message": "The requested membership record could not be found."}, HTTPStatus.NOT_FOUND
        else:
            response, status = (
                membership.update_membership(updated_fields=updated_fields_dict).as_dict(),
                HTTPStatus.OK,
            )

            # if user status changed to active , mail the user
            if membership_status == Status.ACTIVE.name:
                membership.send_notification_to_member(origin, NotificationType.MEMBERSHIP_APPROVED.value)
            elif notify_user and updated_role and updated_role.code != USER and not is_own_membership:
                membership.send_notification_to_member(origin, NotificationType.ROLE_CHANGED.value)

        return response, status
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
        return response, status


@bp.route("/<int:org_id>/members/<int:membership_id>", methods=["DELETE"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def delete_organization_member(org_id, membership_id):  # pylint:disable=unused-argument
    """Mark a membership record as inactive.  Membership must match current user token."""
    try:
        membership = MembershipService.find_membership_by_id(membership_id)

        if membership:
            response, status = membership.deactivate_membership().as_dict(), HTTPStatus.OK
        else:
            response, status = {"message": "The requested membership could not be found."}, HTTPStatus.NOT_FOUND
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code

    return response, status


@bp.route("/<int:org_id>/invitations", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
def get_organization_invitations(org_id):
    """Retrieve the set of invitations for the given org."""
    try:

        invitation_status = request.args.get("status").upper() if request.args.get("status") else None
        invitations = InvitationService.get_invitations_for_org(org_id=org_id, status=invitation_status)

        response, status = {
            "invitations": InvitationSchema(exclude=["membership.org"]).dump(invitations, many=True)
        }, HTTPStatus.OK
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code

    return response, status


@bp.route("/<int:org_id>/admins/affidavits", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_ACCOUNTS.value])
def get_org_admin_affidavit(org_id):
    """Get the affidavit for the admin who created the account."""
    try:
        response, status = AffidavitService.find_affidavit_by_org_id(org_id=org_id), HTTPStatus.OK

    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code

    return response, status


@bp.route("/<int:org_id>/payment_info", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET"])
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
def get_org_payment_info(org_id):
    """Retrieve the set of payment settings associated with the specified org."""
    try:
        org = OrgService.find_by_org_id(org_id, allowed_roles=(*CLIENT_ADMIN_ROLES, STAFF))
        response, status = org.get_payment_info(), HTTPStatus.OK
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status


@bp.route("/<int:org_id>/mailing-address", methods=["PUT"])
@cross_origin(origins="*")
@_jwt.has_one_of_roles(
    [
        Role.SYSTEM.value,
        Role.PUBLIC_USER.value,
        Role.GOV_ACCOUNT_USER.value,
        Role.STAFF_MANAGE_ACCOUNTS.value,
    ]
)
def put_mailing_address(org_id):
    """Update the mailing address specified by the provided id with the request body."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, "org")
    if not valid_format:
        return {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST
    try:
        org = OrgService.find_by_org_id(org_id, allowed_roles=(*CLIENT_ADMIN_ROLES, STAFF, USER))
        if org:
            response, status = org.update_org_address(org_info=request_json).as_dict(), HTTPStatus.OK
        else:
            response, status = {"message": "The requested organization could not be found."}, HTTPStatus.NOT_FOUND
    except BusinessException as exception:
        response, status = {"code": exception.code, "message": exception.message}, exception.status_code
    return response, status

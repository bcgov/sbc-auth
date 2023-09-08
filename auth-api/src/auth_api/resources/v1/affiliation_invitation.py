# Copyright © 2023 Province of British Columbia
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
"""API endpoints for managing an Affiliation Invitation resource."""

from flask import Blueprint, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException, Error
from auth_api.models.dataclass import AffiliationInvitationSearch
from auth_api.schemas import utils as schema_utils
from auth_api.services import AffiliationInvitation as AffiliationInvitationService
from auth_api.services import Entity as EntityService
from auth_api.services import User as UserService
from auth_api.services.authorization import check_auth
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import Role


bp = Blueprint('AFFILIATION_INVITATIONS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/affiliationInvitations')
TRACER = Tracer.get_instance()


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET', 'POST'])
@TRACER.trace()
@_jwt.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
def get_affiliation_invitations():
    """Get affiliation invitations."""
    try:
        get_business_details = request.args.get('businessDetails', 'false')
        org_id = request.args.get('orgId', None)
        business_identifier = request.args.get('businessIdentifier', None)

        search_filter = AffiliationInvitationSearch()
        search_filter.from_org_id = request.args.get('fromOrgId', None)
        search_filter.to_org_id = request.args.get('toOrgId', None)
        search_filter.status_codes = request.args.getlist('statuses')
        search_filter.invitation_types = request.args.getlist('types')
        if business_identifier:
            business = EntityService\
                .find_by_business_identifier(business_identifier=business_identifier, skip_auth=True)
            search_filter.entity_id = business.identifier if business else None

        auth_check_org_id = org_id or search_filter.from_org_id or search_filter.to_org_id
        if not UserService.is_context_user_staff() and check_auth(org_id=auth_check_org_id, disabled_roles=[None]):
            raise BusinessException(Error.NOT_AUTHORIZED_TO_PERFORM_THIS_ACTION, None)

        if org_id:
            data = AffiliationInvitationService. \
                get_all_invitations_with_details_related_to_org(org_id=org_id, search_filter=search_filter)
        else:
            data = AffiliationInvitationService. \
                search_invitations(search_filter=search_filter)

        if get_business_details.lower() == 'true':
            data = AffiliationInvitationService.enrich_affiliation_invitations_dict_list_with_business_data(data)

        response, status = {'affiliationInvitations': data}, http_status.HTTP_200_OK

    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('', methods=['POST'])
@cross_origin(origins='*')
@TRACER.trace()
@_jwt.has_one_of_roles(
    [Role.SYSTEM.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def post_affiliation_invitation():
    """Send a new affiliation invitation using the details in request and saves the affiliation invitation."""
    origin = request.environ.get('HTTP_ORIGIN', 'localhost')
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, 'affiliation_invitation')
    if not valid_format:
        return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST
    try:
        user = UserService.find_by_jwt_token()
        response, status = AffiliationInvitationService.create_affiliation_invitation(request_json,
                                                                                      user, origin)\
            .as_dict(mask_email=True), \
            http_status.HTTP_201_CREATED
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<string:affiliation_invitation_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET', 'PATCH', 'DELETE'])
@TRACER.trace()
@_jwt.requires_auth
def get_affiliation_invitation(affiliation_invitation_id):
    """Get the affiliation invitation specified by the provided id."""
    if not (affiliation_invitation := AffiliationInvitationService.
            find_affiliation_invitation_by_id(affiliation_invitation_id)):
        response, status = {'message': 'The requested affiliation invitation could not be found.'}, \
            http_status.HTTP_404_NOT_FOUND
    else:
        dictionary = affiliation_invitation.as_dict(mask_email=True)
        response, status = dictionary, http_status.HTTP_200_OK
    return response, status


@bp.route('/<string:affiliation_invitation_id>', methods=['PATCH'])
@cross_origin(origins='*')
@TRACER.trace()
@_jwt.has_one_of_roles([Role.STAFF_CREATE_ACCOUNTS.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def patch_affiliation_invitation(affiliation_invitation_id):
    """Update the affiliation invitation specified by the provided id."""
    origin = request.environ.get('HTTP_ORIGIN', 'localhost')
    request_json = request.get_json()
    try:
        affiliation_invitation = AffiliationInvitationService\
            .find_affiliation_invitation_by_id(affiliation_invitation_id)
        if affiliation_invitation is None:
            response, status = {'message': 'The requested affiliation invitation could not be found.'}, \
                http_status.HTTP_404_NOT_FOUND
        else:
            user = UserService.find_by_jwt_token()
            response, status = affiliation_invitation\
                .update_affiliation_invitation(user, origin, request_json).as_dict(mask_email=True),\
                http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<string:affiliation_invitation_id>', methods=['DELETE'])
@cross_origin(origins='*')
@TRACER.trace()
@_jwt.has_one_of_roles(
    [Role.SYSTEM.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def delete_affiliation_invitation(affiliation_invitation_id):
    """Delete the specified affiliation invitation."""
    try:
        AffiliationInvitationService.delete_affiliation_invitation(affiliation_invitation_id)
        response, status = {}, http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<string:affiliation_invitation_id>/token/<string:affiliation_invitation_token>', methods=['PUT', 'OPTIONS'])
@cross_origin(origins='*', methods=['PUT'])
@TRACER.trace()
@_jwt.requires_auth
def accept_affiliation_invitation_token(affiliation_invitation_id, affiliation_invitation_token):
    """Check whether the passed token is valid and add affiliation from the affiliation invitation."""
    origin = request.environ.get('HTTP_ORIGIN', 'localhost')

    try:
        if not (user := UserService.find_by_jwt_token()):
            response, status = {'message': 'Not authorized to perform this action'}, \
                http_status.HTTP_401_UNAUTHORIZED
        else:
            affiliation_invitation_id = AffiliationInvitationService\
                .validate_token(affiliation_invitation_token, int(affiliation_invitation_id)).as_dict().get('id')

            response, status = AffiliationInvitationService\
                .accept_affiliation_invitation(affiliation_invitation_id, user, origin).as_dict(mask_email=True), \
                http_status.HTTP_200_OK

    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<string:affiliation_invitation_id>/authorization/<string:authorize_action>', methods=['PATCH', 'OPTIONS'])
@cross_origin(origins='*', methods=['PATCH'])
@TRACER.trace()
@_jwt.requires_auth
def patch_affiliation_invitation_authorization(affiliation_invitation_id, authorize_action):
    """Check if user is active part of the Org. Authorize/Refuse Authorization invite if he is."""
    origin = request.environ.get('HTTP_ORIGIN', 'localhost')

    try:
        user = UserService.find_by_jwt_token()
        _verify_permissions(user=user, affiliation_invitation_id=affiliation_invitation_id)

        if authorize_action == 'accept':
            response, status = AffiliationInvitationService \
                .accept_affiliation_invitation(affiliation_invitation_id=affiliation_invitation_id,
                                               user=user,
                                               origin=origin).as_dict(mask_email=True), \
                http_status.HTTP_200_OK
        elif authorize_action == 'refuse':
            response, status = AffiliationInvitationService \
                .refuse_affiliation_invitation(invitation_id=affiliation_invitation_id, user=user)\
                .as_dict(mask_email=True), \
                http_status.HTTP_200_OK
        else:
            err = {'code': 400, 'message': f'{authorize_action} is not supported on this endpoint'}
            raise BusinessException(err, http_status.HTTP_400_BAD_REQUEST)

    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

    return response, status


def _verify_permissions(user, affiliation_invitation_id):
    if not user:
        raise BusinessException(Error.NOT_AUTHORIZED_TO_PERFORM_THIS_ACTION, None)

    affiliation_invitation = AffiliationInvitationService. \
        find_affiliation_invitation_by_id(affiliation_invitation_id)
    if not affiliation_invitation:
        raise BusinessException(Error.DATA_NOT_FOUND, None)

    to_org_id = affiliation_invitation.as_dict()['to_org']['id']
    if not UserService.is_user_member_of_org(user=user, org_id=to_org_id):
        raise BusinessException(Error.NOT_AUTHORIZED_TO_PERFORM_THIS_ACTION, None)

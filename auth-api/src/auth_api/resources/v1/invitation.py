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

from flask import Blueprint, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.schemas import utils as schema_utils
from auth_api.services import Invitation as InvitationService
from auth_api.services import User as UserService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import Role


bp = Blueprint('INVITATIONS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/invitations')
TRACER = Tracer.get_instance()


@bp.route('', methods=['POST'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.has_one_of_roles(
    [Role.SYSTEM.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def post_invitation():
    """Send a new invitation using the details in request and saves the invitation."""
    origin = request.environ.get('HTTP_ORIGIN', 'localhost')
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, 'invitation')
    if not valid_format:
        return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST
    try:
        user = UserService.find_by_jwt_token()
        response, status = InvitationService.create_invitation(request_json, user, origin).as_dict(), \
            http_status.HTTP_201_CREATED
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<string:invitation_id>', methods=['GET', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def get_invitation(invitation_id):
    """Get the invitation specified by the provided id."""
    invitation = InvitationService.find_invitation_by_id(invitation_id)
    if invitation is None:
        response, status = {'message': 'The requested invitation could not be found.'}, \
                           http_status.HTTP_404_NOT_FOUND
    else:
        response, status = invitation.as_dict(), http_status.HTTP_200_OK
    return response, status


@bp.route('/<string:invitation_id>', methods=['PATCH'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.has_one_of_roles([Role.STAFF_CREATE_ACCOUNTS.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def patch_invitation(invitation_id):
    """Update the invitation specified by the provided id as retried."""
    origin = request.environ.get('HTTP_ORIGIN', 'localhost')
    try:
        invitation = InvitationService.find_invitation_by_id(invitation_id)
        if invitation is None:
            response, status = {'message': 'The requested invitation could not be found.'}, \
                               http_status.HTTP_404_NOT_FOUND
        else:
            user = UserService.find_by_jwt_token()
            response, status = invitation.update_invitation(user, origin).as_dict(), http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<string:invitation_id>', methods=['DELETE'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.has_one_of_roles(
    [Role.SYSTEM.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def delete_invitation(invitation_id):
    """Delete the specified invitation."""
    try:
        InvitationService.delete_invitation(invitation_id)
        response, status = {}, http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/tokens/<string:invitation_token>', methods=['GET', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
def validate_invitation_token(invitation_token):
    """Check whether the passed token is valid."""
    try:
        InvitationService.validate_token(invitation_token)
        response, status = {}, http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/tokens/<string:invitation_token>', methods=['PUT'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def accept_invitation_token(invitation_token):
    """Check whether the passed token is valid and add user, role and org from invitation to membership."""
    origin = request.environ.get('HTTP_ORIGIN', 'localhost')

    try:
        user = UserService.find_by_jwt_token()
        if user is None:
            response, status = {'message': 'Not authorized to perform this action'}, \
                               http_status.HTTP_401_UNAUTHORIZED
        else:
            invitation_id = InvitationService.validate_token(invitation_token).as_dict().get('id')
            response, status = InvitationService.accept_invitation(invitation_id, user, origin).as_dict(), \
                               http_status.HTTP_200_OK  # noqa:E127

    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status

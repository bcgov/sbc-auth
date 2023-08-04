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

from flask import request
from flask_restx import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.schemas import utils as schema_utils
from auth_api.services import AffiliationInvitation as AffiliationInvitationService
from auth_api.services import User as UserService
from auth_api.tracer import Tracer
from auth_api.utils.roles import Role
from auth_api.utils.util import cors_preflight


API = Namespace('invitations', description='Endpoints for affiliation invitations management')
TRACER = Tracer.get_instance()


@cors_preflight('GET,POST,OPTIONS')
@API.route('', methods=['GET', 'POST', 'OPTIONS'])
class AffiliationInvitations(Resource):
    """Resource for managing AffiliationInvitations."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.has_one_of_roles(
        [Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def get():
        """Get affiliation invitations."""
        try:
            org_id = request.args.get('orgId', None)
            status = request.args.get('status', None)
            data = AffiliationInvitationService.search_invitations_for_from_org(org_id, status)
            data = data or {'affiliationInvitations': []}

            response, status = data, http_status.HTTP_200_OK

        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.has_one_of_roles(
        [Role.SYSTEM.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def post():
        """Send a new affiliation invitation using the details in request and saves the affiliation invitation."""
        origin = request.environ.get('HTTP_ORIGIN', 'localhost')
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'affiliation_invitation')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST
        try:
            user = UserService.find_by_jwt_token()
            response, status = AffiliationInvitationService.create_affiliation_invitation(request_json,
                                                                                          user, origin).as_dict(), \
                http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('GET,PATCH,DELETE,OPTIONS')
@API.route('/<string:affiliation_invitation_id>', methods=['GET', 'PATCH', 'DELETE', 'OPTIONS'])
class AffiliationInvitation(Resource):
    """Resource for managing a single affiliation invitation."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.requires_auth
    def get(affiliation_invitation_id):
        """Get the affiliation invitation specified by the provided id."""
        if not (affiliation_invitation := AffiliationInvitationService.
                find_affiliation_invitation_by_id(affiliation_invitation_id)):
            response, status = {'message': 'The requested affiliation invitation could not be found.'}, \
                http_status.HTTP_404_NOT_FOUND
        else:
            response, status = affiliation_invitation.as_dict(), http_status.HTTP_200_OK
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.has_one_of_roles([Role.STAFF_CREATE_ACCOUNTS.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def patch(affiliation_invitation_id):
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
                    .update_affiliation_invitation(user, origin, request_json).as_dict(),\
                    http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.has_one_of_roles(
        [Role.SYSTEM.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def delete(affiliation_invitation_id):
        """Delete the specified affiliation invitation."""
        try:
            AffiliationInvitationService.delete_affiliation_invitation(affiliation_invitation_id)
            response, status = {}, http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('GET,PUT,OPTIONS')
@API.route('/<string:affiliation_invitation_id>/token/<string:affiliation_invitation_token>',
           methods=['PUT', 'OPTIONS'])
class InvitationAction(Resource):
    """Check for a valid token and accept an affiliation invitation token."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.requires_auth
    def put(affiliation_invitation_id, affiliation_invitation_token):
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
                    .accept_affiliation_invitation(affiliation_invitation_id, user, origin).as_dict(), \
                    http_status.HTTP_200_OK

        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

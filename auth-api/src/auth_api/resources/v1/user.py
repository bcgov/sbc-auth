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
"""API endpoints for managing a User resource."""

from flask import Blueprint, abort, g, jsonify, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.schemas import MembershipSchema, OrgSchema
from auth_api.schemas import utils as schema_utils
from auth_api.services import Affidavit as AffidavitService
from auth_api.services import Invitation as InvitationService
from auth_api.services.authorization import Authorization as AuthorizationService
from auth_api.services.keycloak import KeycloakService
from auth_api.services.membership import Membership as MembershipService
from auth_api.services.org import Org as OrgService
from auth_api.services.user import User as UserService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.enums import LoginSource, Status
from auth_api.utils.roles import Role


bp = Blueprint('USERS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/users')
TRACER = Tracer.get_instance()


@bp.route('/bcros', methods=['POST', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
def post_anonymous_user():
    """Post a new user using the request body who has a proper invitation."""
    try:
        request_json = request.get_json()
        invitation_token = request.headers.get('invitation_token', None)
        invitation = InvitationService.validate_token(invitation_token).as_dict()

        valid_format, errors = schema_utils.validate(request_json, 'anonymous_user')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        membership_details = {
            'email': invitation['recipient_email'],
            'membershipType': invitation['membership'][0]['membership_type'],
            'update_password_on_login': False
        }
        membership_details.update(request_json)
        user = UserService.create_user_and_add_membership([membership_details],
                                                          invitation['membership'][0]['org']['id'],
                                                          single_mode=True)
        user_dict = user['users'][0]
        if user_dict['http_status'] != http_status.HTTP_201_CREATED:
            response, status = {'code': user_dict['http_status'], 'message': user_dict['error']}, user_dict[
                'http_status']
        else:
            InvitationService.accept_invitation(invitation['id'], None, None, False)
            response, status = user, http_status.HTTP_201_CREATED

    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('', methods=['POST'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def post_user():
    """Post a new user using the request body (which will contain a JWT).

    If the user already exists, update the name.
    """
    token = g.jwt_oidc_token_info

    try:
        request_json = request.get_json(silent=True)
        # For BCeID users validate schema.
        if token.get('loginSource', None) == LoginSource.BCEID.value and request_json is not None:
            valid_format, errors = schema_utils.validate(request_json, 'user')
            if not valid_format:
                return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        user = UserService.save_from_jwt_token(request_json)
        response, status = user.as_dict(), http_status.HTTP_201_CREATED
        # Add the user to public_users group if the user doesn't have public_user group
        if token.get('loginSource', '') != LoginSource.STAFF.value:
            KeycloakService.join_users_group()
        # For anonymous users, there are no invitation process for members,
        # so whenever they login perform this check and add them to corresponding groups
        if token.get('loginSource', '') == LoginSource.BCROS.value:
            if len(OrgService.get_orgs(user.identifier, [Status.ACTIVE.value])) > 0:
                KeycloakService.join_account_holders_group()
        if user.type == Role.STAFF.name:
            MembershipService.add_staff_membership(user.identifier)
        else:
            MembershipService.remove_staff_membership(user.identifier)

    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('', methods=['GET', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.has_one_of_roles([Role.STAFF_VIEW_ACCOUNTS.value])
def get_user():
    """Return a set of users based on search query parameters (staff only)."""
    search_email = request.args.get('email', '')
    search_first_name = request.args.get('firstname', '')
    search_last_name = request.args.get('lastname', '')

    users = UserService.find_users(first_name=search_first_name, last_name=search_last_name, email=search_email)
    collection = []
    for user in users:
        collection.append(UserService(user).as_dict())
    response = jsonify(collection)
    status = http_status.HTTP_200_OK
    return response, status


@bp.route('/<path:username>/otp', methods=['GET', 'OPTIONS', 'DELETE'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.has_one_of_roles([Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value, Role.STAFF_VIEW_ACCOUNTS.value])
def delete_user_otp(username):
    """Delete/Reset the OTP of user profile associated with the provided username."""
    try:
        user = UserService.find_by_username(username)
        if user is None:
            response, status = {'message': f'User {username} does not exist.'}, http_status.HTTP_404_NOT_FOUND
        elif user.as_dict().get('login_source', None) != LoginSource.BCEID.value:
            response, status = {'Only BCEID users has OTP', http_status.HTTP_400_BAD_REQUEST}
        else:
            origin_url = request.environ.get('HTTP_ORIGIN', 'localhost')
            UserService.delete_otp_for_user(username, origin_url=origin_url)
            response, status = '', http_status.HTTP_204_NO_CONTENT
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<path:username>', methods=['GET', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def get_by_username(username):
    """Return the user profile associated with the provided username."""
    user = UserService.find_by_username(username)
    if user is None:
        response, status = jsonify({'message': f'User {username} does not exist.'}), http_status.HTTP_404_NOT_FOUND
    else:
        response, status = user.as_dict(), http_status.HTTP_200_OK
    return response, status


@bp.route('/<path:username>', methods=['DELETE'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def delete_by_username(username):
    """Delete the user profile associated with the provided username."""
    try:
        user = UserService.find_by_username(username)
        if user is None:
            response, status = {'message': f'User {username} does not exist.'}, http_status.HTTP_404_NOT_FOUND
        elif user.as_dict().get('type', None) != Role.ANONYMOUS_USER.name:
            response, status = {'Normal users cant be deleted', http_status.HTTP_501_NOT_IMPLEMENTED}
        else:
            UserService.delete_anonymous_user(username)
            response, status = '', http_status.HTTP_204_NO_CONTENT
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<path:username>', methods=['PATCH'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def patch_by_username(username):
    """Patch the user profile associated with the provided username.

    User only for patching the password.
    """
    try:

        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'anonymous_user')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST
        user = UserService.find_by_username(username)

        if user is None:
            response, status = jsonify({'message': f'User {username} does not exist.'}), http_status.HTTP_404_NOT_FOUND
        elif user.as_dict().get('type', None) != Role.ANONYMOUS_USER.name:
            response, status = {'Normal users cant be patched', http_status.HTTP_501_NOT_IMPLEMENTED}
        else:
            UserService.reset_password_for_anon_user(request_json, username)
            response, status = '', http_status.HTTP_204_NO_CONTENT
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/@me', methods=['GET', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def get_current_user():
    """Return the user profile associated with the JWT in the authorization header."""
    try:
        response, status = UserService.find_by_jwt_token().as_dict(), http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/@me', methods=['PATCH'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def patch_current_user():
    """Update terms of service for the user."""
    request_json = request.get_json()

    valid_format, errors = schema_utils.validate(request_json, 'termsofuse')
    if not valid_format:
        return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

    version = request_json['termsversion']
    is_terms_accepted = request_json['istermsaccepted']
    try:
        response, status = UserService.update_terms_of_use(is_terms_accepted, version).as_dict(), \
                           http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/@me', methods=['DELETE'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def delete_current_user():
    """Delete the user profile."""
    try:
        UserService.delete_user()
        response, status = '', http_status.HTTP_204_NO_CONTENT
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/contacts', methods=['GET', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def get_user_contacts():
    """Retrieve the set of contacts asociated with the current user identifier by the JWT in the header."""
    token = g.jwt_oidc_token_info
    if not token:
        return {'message': 'Authorization required.'}, http_status.HTTP_401_UNAUTHORIZED

    try:
        response, status = UserService.get_contacts(), http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/contacts', methods=['POST'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def post_user_contact():
    """Create a new contact for the user associated with the JWT in the authorization header."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, 'contact')
    if not valid_format:
        return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

    try:
        response, status = UserService.add_contact(request_json).as_dict(), http_status.HTTP_201_CREATED
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/contacts', methods=['PUT'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def put_user_contact():
    """Update an existing contact for the user associated with the JWT in the authorization header."""
    request_json = request.get_json()
    valid_format, errors = schema_utils.validate(request_json, 'contact')
    if not valid_format:
        return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST
    try:
        response, status = UserService.update_contact(request_json).as_dict(), http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/contacts', methods=['DELETE'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def delete_user_contact():
    """Delete the contact info for the user associated with the JWT in the authorization header."""
    try:
        response, status = UserService.delete_contact().as_dict(), http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/orgs', methods=['GET', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.has_one_of_roles([Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
def get_user_organizations():
    """Get a list of orgs that the current user is associated with."""
    try:
        user = UserService.find_by_jwt_token()
        if not user:
            response, status = {'message': 'User not found.'}, http_status.HTTP_404_NOT_FOUND
        else:
            all_orgs = OrgService.get_orgs(user.identifier)
            orgs = OrgSchema().dump(
                all_orgs, many=True)
            response, status = jsonify({'orgs': orgs}), http_status.HTTP_200_OK

    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/orgs/<int:org_id>/membership', methods=['GET', 'OPTIONS'])
@_jwt.has_one_of_roles([Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
@cross_origin(origin='*')
def get_user_org_membership(org_id):
    """Get the membership for the given org and user."""
    try:
        user = UserService.find_by_jwt_token()
        if not user:
            response, status = {'message': 'User not found.'}, http_status.HTTP_404_NOT_FOUND
        else:
            membership = MembershipService \
                .get_membership_for_org_and_user_all_status(org_id=org_id, user_id=user.identifier)
            response, status = MembershipSchema(exclude=['org']).dump(membership), http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<string:user_guid>/affidavits', methods=['POST'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def post_user_affidavit(user_guid):
    """Create affidavit record for the user."""
    token = g.jwt_oidc_token_info
    request_json = request.get_json()

    if token.get('sub', None) != user_guid:
        abort(403)
    valid_format, errors = schema_utils.validate(request_json, 'affidavit')
    if not valid_format:
        return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

    try:
        response, status = AffidavitService.create_affidavit(request_json).as_dict(), http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<string:user_guid>/affidavits', methods=['GET', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.has_one_of_roles([Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
def get_user_affidavit(user_guid):
    """Return pending/active affidavit for the user."""
    token = g.jwt_oidc_token_info
    affidavit_status = request.args.get('status', None)

    if Role.STAFF.value not in token['realm_access']['roles'] and token.get('sub', None) != user_guid:
        abort(403)

    try:
        response, status = AffidavitService.find_affidavit_by_user_guid(user_guid, status=affidavit_status), \
                           http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/authorizations', methods=['GET', 'OPTIONS'])
@_jwt.requires_auth
@cross_origin(origin='*')
def get_user_authorizations():
    """Add a new contact for the Entity identified by the provided id."""
    sub = g.jwt_oidc_token_info.get('sub', None)
    return AuthorizationService.get_user_authorizations(sub), http_status.HTTP_200_OK

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

from flask import g, jsonify, request
from flask_restplus import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.schemas import InvitationSchema, MembershipSchema
from auth_api.schemas import utils as schema_utils
from auth_api.services import Affidavit as AffidavitService
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import Invitation as InvitationService
from auth_api.services import Membership as MembershipService
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService
from auth_api.tracer import Tracer
from auth_api.utils.enums import AccessType, AffidavitStatus, ChangeType, NotificationType, Status
from auth_api.utils.roles import ALL_ALLOWED_ROLES, CLIENT_ADMIN_ROLES, STAFF, USER, Role
from auth_api.utils.util import cors_preflight

API = Namespace('orgs', description='Endpoints for organization management')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET,POST,OPTIONS')
@API.route('', methods=['GET', 'POST', 'OPTIONS'])
class Orgs(Resource):
    """Resource for managing orgs."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.PUBLIC_USER.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.SYSTEM.value])
    def post():
        """Post a new org using the request body.

        If the org already exists, update the attributes.
        """
        token = g.jwt_oidc_token_info
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'org')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST
        try:
            user = UserService.find_by_jwt_token(token)
            if user is None:
                response, status = {'message': 'Not authorized to perform this action'}, \
                                   http_status.HTTP_401_UNAUTHORIZED
                return response, status
            bearer_token = request.headers['Authorization'].replace('Bearer ', '')
            origin_url = request.environ.get('HTTP_ORIGIN', 'localhost')
            response, status = OrgService.create_org(request_json, user.identifier, token,
                                                     bearer_token=bearer_token,
                                                     origin_url=origin_url).as_dict(), http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def get():
        """Search orgs."""
        # Search based on request arguments
        business_identifier = request.args.get('affiliation', None)
        name = request.args.get('name', None)
        status = request.args.get('status', None)
        access_type = request.args.get('access_type', None)
        bcol_account_id = request.args.get('bcolAccountId', None)
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        validate_name = request.args.get('validateName', 'False')

        try:
            token = g.jwt_oidc_token_info
            if validate_name.upper() == 'TRUE':
                response, status = OrgService.find_by_org_name(name), http_status.HTTP_200_OK
            else:
                response, status = OrgService.search_orgs(business_identifier=business_identifier,
                                                          access_type=access_type, name=name,
                                                          status=status, bcol_account_id=bcol_account_id, page=page,
                                                          limit=limit, token=token), http_status.HTTP_200_OK

            # If public user is searching , return 200 with empty results if orgs exist
            # Else return 204

            is_public_user = Role.PUBLIC_USER.value in token.get('realm_access').get('roles')
            if is_public_user:  # public user cant get the details in search.Gets only status of orgs
                if response and response.get('orgs'):
                    status = http_status.HTTP_200_OK
                else:
                    status = http_status.HTTP_204_NO_CONTENT
                response = {}  # Do not return any results if searching by name

        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('GET,PUT,OPTIONS,DELETE')
@API.route('/<string:org_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
class Org(Resource):
    """Resource for managing a single org."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def get(org_id):
        """Get the org specified by the provided id."""
        org = OrgService.find_by_org_id(org_id, g.jwt_oidc_token_info, allowed_roles=ALL_ALLOWED_ROLES)
        if org is None:
            response, status = {'message': 'The requested organization could not be found.'}, \
                               http_status.HTTP_404_NOT_FOUND
        else:
            response, status = org.as_dict(), http_status.HTTP_200_OK
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles(
        [Role.SYSTEM.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def put(org_id):
        """Update the org specified by the provided id with the request body."""
        request_json = request.get_json()
        action = request.args.get('action', '').upper()
        valid_format, errors = schema_utils.validate(request_json, 'org')
        token = g.jwt_oidc_token_info
        bearer_token = request.headers['Authorization'].replace('Bearer ', '')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST
        try:
            org = OrgService.find_by_org_id(org_id, g.jwt_oidc_token_info,
                                            allowed_roles=(*CLIENT_ADMIN_ROLES, STAFF))
            if org and org.as_dict().get('accessType', None) == AccessType.ANONYMOUS.value and \
                    Role.STAFF_CREATE_ACCOUNTS.value not in token.get('realm_access').get('roles'):
                return {'message': 'The organisation can only be updated by a staff admin.'}, \
                       http_status.HTTP_401_UNAUTHORIZED
            if org:
                if action in (ChangeType.DOWNGRADE.value, ChangeType.UPGRADE.value):
                    response, status = org.change_org_ype(request_json, action,
                                                          bearer_token).as_dict(), http_status.HTTP_200_OK
                else:
                    response, status = org.update_org(request_json, bearer_token).as_dict(), http_status.HTTP_200_OK
            else:
                response, status = {'message': 'The requested organization could not be found.'}, \
                                   http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def delete(org_id):
        """Inactivates the org if it has no active members or affiliations."""
        token = g.jwt_oidc_token_info
        try:
            OrgService.delete_org(org_id, token)
            response, status = '', http_status.HTTP_204_NO_CONTENT
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('GET,POST,PUT,OPTIONS')
@API.route('/<string:org_id>/login-options', methods=['GET', 'POST', 'PUT', 'OPTIONS'])
class OrgLoginOptions(Resource):
    """Resource for managing org login options."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def get(org_id):
        """Retrieve the set of payment settings associated with the specified org."""
        try:
            login_options = OrgService.get_login_options_for_org(org_id, g.jwt_oidc_token_info,
                                                                 allowed_roles=ALL_ALLOWED_ROLES)
            response, status = jsonify(
                {'loginOption': login_options.login_source if login_options else None}), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def post(org_id):
        """Create a new login type for the specified org."""
        request_json = request.get_json()
        login_option_val = request_json.get('loginOption')
        # TODO may be add validation here
        try:
            login_option = OrgService.add_login_option(org_id, login_option_val, g.jwt_oidc_token_info)
            response, status = jsonify({'login_option': login_option.login_source}), http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def put(org_id):
        """Update a new login type for the specified org."""
        request_json = request.get_json()
        login_option_val = request_json.get('loginOption')
        # TODO may be add validation here
        try:
            login_option = OrgService.update_login_option(org_id, login_option_val, g.jwt_oidc_token_info)
            response, status = jsonify({'login_option': login_option.login_source}), http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('GET,DELETE,POST,PUT,OPTIONS')
@API.route('/<string:org_id>/contacts', methods=['GET', 'DELETE', 'POST', 'PUT', 'OPTIONS'])
class OrgContacts(Resource):
    """Resource for managing org contacts."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def get(org_id):
        """Retrieve the set of contacts associated with the specified org."""
        try:
            response, status = OrgService.get_contacts(org_id), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_CREATE_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def post(org_id):
        """Create a new contact for the specified org."""
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'contact')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            response, status = OrgService.add_contact(org_id, request_json).as_dict(), http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def put(org_id):
        """Update an existing contact for the specified org."""
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'contact')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST
        try:
            response, status = OrgService.update_contact(org_id, request_json).as_dict(), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def delete(org_id):
        """Delete the contact info for the specified org."""
        try:
            response, status = OrgService.delete_contact(org_id).as_dict(), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('GET,POST,OPTIONS')
@API.route('/<string:org_id>/affiliations', methods=['GET', 'POST', 'OPTIONS'])
class OrgAffiliations(Resource):
    """Resource for managing affiliations for an org."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_BUSINESS.value, Role.PUBLIC_USER.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def post(org_id):
        """Post a new Affiliation for an org using the request body."""
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'affiliation')
        bearer_token = request.headers['Authorization'].replace('Bearer ', '')
        is_new_business = request.args.get('newBusiness', 'false').lower() == 'true'
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            if is_new_business:
                response, status = AffiliationService.create_new_business_affiliation(
                    org_id, request_json.get('businessIdentifier'), request_json.get('email'),
                    request_json.get('phone'),
                    token_info=g.jwt_oidc_token_info, bearer_token=bearer_token).as_dict(), http_status.HTTP_201_CREATED
            else:
                response, status = AffiliationService.create_affiliation(
                    org_id, request_json.get('businessIdentifier'), request_json.get('passCode'),
                    token_info=g.jwt_oidc_token_info).as_dict(), http_status.HTTP_201_CREATED

        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

        return response, status

    @staticmethod
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_BUSINESS.value, Role.PUBLIC_USER.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get(org_id):
        """Get all affiliated entities for the given org."""
        try:
            response, status = jsonify({
                'entities': AffiliationService.find_affiliated_entities_by_org_id(org_id, g.jwt_oidc_token_info)}), \
                               http_status.HTTP_200_OK

        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

        return response, status


@cors_preflight('DELETE,OPTIONS')
@API.route('/<string:org_id>/affiliations/<string:business_identifier>', methods=['DELETE', 'OPTIONS'])
class OrgAffiliation(Resource):
    """Resource for managing a single affiliation between an org and an entity."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_BUSINESS.value, Role.PUBLIC_USER.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def delete(org_id, business_identifier):
        """Delete an affiliation between an org and an entity."""
        try:
            AffiliationService.delete_affiliation(org_id, business_identifier, g.jwt_oidc_token_info)
            response, status = {}, http_status.HTTP_200_OK

        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, \
                               exception.status_code

        return response, status


@cors_preflight('GET,OPTIONS')
@API.route('/<string:org_id>/members', methods=['GET', 'OPTIONS'])
class OrgMembers(Resource):
    """Resource for managing a set of members for a single organization."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get(org_id):
        """Retrieve the set of members for the given org."""
        try:

            status = request.args.get('status').upper() if request.args.get('status') else None
            roles = request.args.get('roles').upper() if request.args.get('roles') else None

            members = MembershipService.get_members_for_org(org_id, status=status,
                                                            membership_roles=roles, token_info=g.jwt_oidc_token_info)
            if members:
                response, status = {'members': MembershipSchema(exclude=['org']).dump(members, many=True)}, \
                                   http_status.HTTP_200_OK
            else:
                response, status = {}, \
                                   http_status.HTTP_200_OK

        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

        return response, status


@cors_preflight('DELETE,PATCH,OPTIONS')
@API.route('/<string:org_id>/members/<string:membership_id>', methods=['DELETE', 'PATCH', 'OPTIONS'])
class OrgMember(Resource):
    """Resource for managing a single membership record between an org and a user."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def patch(org_id, membership_id):  # pylint:disable=unused-argument
        """Update a membership record with new member role."""
        token = g.jwt_oidc_token_info
        role = request.get_json().get('role')
        membership_status = request.get_json().get('status')
        notify_user = request.get_json().get('notifyUser')
        updated_fields_dict = {}
        origin = request.environ.get('HTTP_ORIGIN', 'localhost')
        try:
            if role is not None:
                updated_role = MembershipService.get_membership_type_by_code(role)
                updated_fields_dict['membership_type'] = updated_role
            if membership_status is not None:
                updated_fields_dict['membership_status'] = \
                    MembershipService.get_membership_status_by_code(membership_status)

            membership = MembershipService.find_membership_by_id(membership_id, token)

            is_own_membership = membership.as_dict()['user']['username'] == \
                UserService.find_by_jwt_token(token).as_dict()['username']
            if not membership:
                response, status = {'message': 'The requested membership record could not be found.'}, \
                                   http_status.HTTP_404_NOT_FOUND
            else:
                response, status = membership.update_membership(updated_fields=updated_fields_dict, token_info=token
                                                                ).as_dict(), http_status.HTTP_200_OK

                # if user status changed to active , mail the user
                if membership_status == Status.ACTIVE.name:
                    membership.send_notification_to_member(origin, NotificationType.MEMBERSHIP_APPROVED.value)
                elif notify_user and updated_role and updated_role.code != USER and not is_own_membership:
                    membership.send_notification_to_member(origin, NotificationType.ROLE_CHANGED.value)

            return response, status
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
            return response, status

    @staticmethod
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_ACCOUNTS.value, Role.PUBLIC_USER.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def delete(org_id, membership_id):  # pylint:disable=unused-argument
        """Mark a membership record as inactive.  Membership must match current user token."""
        token = g.jwt_oidc_token_info
        try:
            membership = MembershipService.find_membership_by_id(membership_id, token)

            if membership:
                response, status = membership.deactivate_membership(token).as_dict(), \
                                   http_status.HTTP_200_OK
            else:
                response, status = {'message': 'The requested membership could not be found.'}, \
                                   http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

        return response, status


@cors_preflight('GET,OPTIONS')
@API.route('/<string:org_id>/invitations', methods=['GET', 'OPTIONS'])
class OrgInvitations(Resource):
    """Resource for managing a set of invitations for a single organization."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get(org_id):
        """Retrieve the set of invitations for the given org."""
        try:

            invitation_status = request.args.get('status').upper() if request.args.get('status') else None
            invitations = InvitationService.get_invitations_for_org(org_id=org_id,
                                                                    status=invitation_status,
                                                                    token_info=g.jwt_oidc_token_info)

            response, status = {'invitations': InvitationSchema().dump(invitations, many=True)}, http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

        return response, status


@cors_preflight('GET,OPTIONS')
@API.route('/<string:org_id>/admins/affidavits', methods=['GET', 'PATCH', 'OPTIONS'])
class OrgAdminAffidavits(Resource):
    """Resource for managing affidavits for the admins in an org."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_ACCOUNTS.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get(org_id):
        """Get the affidavit for the admin who created the account."""
        try:
            response, status = AffidavitService.find_affidavit_by_org_id(org_id=org_id), \
                               http_status.HTTP_200_OK

        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

        return response, status


@cors_preflight('PATCH,OPTIONS')
@API.route('/<string:org_id>/status', methods=['PATCH', 'OPTIONS'])
class OrgStatus(Resource):
    """Resource for changing the status of org."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_MANAGE_ACCOUNTS.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def patch(org_id):
        """Patch an account."""
        request_json = request.get_json()
        token = g.jwt_oidc_token_info
        # For now allowed is to put the status code, which will be done by bcol_staff_admin.
        # If this patch is going to be used by other other roles, then add proper security check

        try:
            is_approved: bool = request_json.get('statusCode', None) == AffidavitStatus.APPROVED.value
            origin = request.environ.get('HTTP_ORIGIN', 'localhost')
            response, status = OrgService.approve_or_reject(org_id=org_id, is_approved=is_approved,
                                                            token_info=token,
                                                            origin_url=origin).as_dict(), http_status.HTTP_200_OK

        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

        return response, status


@cors_preflight('GET,OPTIONS')
@API.route('/<string:org_id>/payment_info', methods=['GET', 'OPTIONS'])
class OrgPaymentSettings(Resource):
    """Resource for getting org payment info."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.SYSTEM.value, Role.STAFF_VIEW_ACCOUNTS.value, Role.PUBLIC_USER.value])
    def get(org_id):
        """Retrieve the set of payment settings associated with the specified org."""
        try:
            org = OrgService.find_by_org_id(org_id, g.jwt_oidc_token_info,
                                            allowed_roles=(*CLIENT_ADMIN_ROLES, STAFF))
            response, status = org.get_payment_info(), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

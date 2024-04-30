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
"""The User service.

This module manages the User Information.
"""

import json
from typing import Dict, List

from flask import current_app
from jinja2 import Environment, FileSystemLoader
from requests import HTTPError
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api import status as http_status
from auth_api.models.dataclass import Activity
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import User as UserModel
from auth_api.models import db
from auth_api.schemas import UserSchema

from auth_api.services.authorization import check_auth
from auth_api.services.keycloak_user import KeycloakUser
from auth_api.utils import util
from auth_api.utils.enums import (
    AccessType, ActivityAction, DocumentType, IdpHint, LoginSource, OrgStatus, QueueMessageTypes, Status, UserStatus)
from auth_api.utils.roles import ADMIN, CLIENT_ADMIN_ROLES, COORDINATOR, STAFF, Role
from auth_api.utils.user_context import UserContext, user_context
from auth_api.utils.util import camelback2snake

from ..utils.account_mailer import publish_to_mailer
from .activity_log_publisher import ActivityLogPublisher
from .contact import Contact as ContactService
from .documents import Documents as DocumentService
from .keycloak import KeycloakService


ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class User:  # pylint: disable=too-many-instance-attributes disable=too-many-public-methods
    """Manages all aspects of the User Entity.

    This manages storing the User in the cache,
    ensuring that the local cache is up to date,
    submitting changes back to all storage systems as needed.
    """

    def __init__(self, model):
        """Return a User Service object."""
        self._model: UserModel = model

    @property
    def identifier(self):
        """Return the identifier for this user."""
        return self._model.id

    @property
    def keycloak_guid(self) -> str:
        """Return the Keycloak GUID for the user."""
        return self._model.keycloak_guid

    @property
    def verified(self) -> str:
        """Return the verified flag for the user."""
        return self._model.verified

    @property
    def type(self) -> str:
        """Return the type for the user."""
        return self._model.type

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the User as a python dict.

        None fields are not included in the dict.
        """
        user_schema = UserSchema()
        obj = user_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    def create_user_and_add_membership(memberships: List[dict], org_id,
                                       # pylint: disable=too-many-locals, too-many-statements, too-many-branches
                                       single_mode: bool = False):
        """
        Create user(s) in the  DB and upstream keycloak.

        accepts a list of memberships ie.a list of objects with username,password and membershipTpe
        single_mode can be used if called method already perfomed the authenticaiton
        single_mode= true is used now incase of invitation for admin users scenarion
        other cases should be invoked with single_mode=false
        """
        User._validate_and_throw_exception(memberships, org_id, single_mode)

        current_app.logger.debug('create_user')
        users = []
        for membership in memberships:
            username = membership['username']
            current_app.logger.debug(f'create user username: {username}')
            create_user_request = User._create_kc_user(membership)
            db_username = IdpHint.BCROS.value + '/' + username
            user_model = UserModel.find_by_username(db_username)
            re_enable_user = False
            existing_kc_user = KeycloakService.get_user_by_username(username)
            enabled_in_kc = getattr(existing_kc_user, 'enabled', True)
            if getattr(user_model, 'status', None) == Status.INACTIVE.value and not enabled_in_kc:
                membership_model = MembershipModel.find_membership_by_userid(user_model.id)
                re_enable_user = membership_model.org_id == org_id
            if user_model and not re_enable_user:
                current_app.logger.debug('Existing users found in DB')
                users.append(User._get_error_dict(username, Error.USER_ALREADY_EXISTS))
                continue

            if membership.get('update_password_on_login', True):  # by default , reset needed
                create_user_request.update_password_on_login()
            try:
                if re_enable_user:
                    kc_user = KeycloakService.update_user(create_user_request)
                else:
                    kc_user = KeycloakService.add_user(create_user_request, throw_error_if_exists=True)
            except BusinessException as err:
                current_app.logger.error('create_user in keycloak failed :duplicate user %s', err)
                users.append(User._get_error_dict(username, Error.USER_ALREADY_EXISTS))
                continue
            except HTTPError as err:
                current_app.logger.error('create_user in keycloak failed %s', err)
                users.append(User._get_error_dict(username, Error.FAILED_ADDING_USER_ERROR))
                continue
            try:
                if re_enable_user:
                    user_model.status = Status.ACTIVE.value
                    user_model.type = Role.ANONYMOUS_USER.name
                    user_model.login_source = LoginSource.BCROS.value
                    user_model.flush()
                    membership_model.status = Status.ACTIVE.value
                    membership_model.membership_type_code = membership['membershipType']
                    membership_model.flush()
                else:
                    user_model = User._create_new_user_and_membership(db_username, kc_user, membership, org_id)

                db.session.commit()  # commit is for session ;need not to invoke for every object
                user_dict = User(user_model).as_dict()
                user_dict.update({'http_status': http_status.HTTP_201_CREATED, 'error': ''})
                users.append(user_dict)
            except Exception as e:  # NOQA # pylint: disable=broad-except
                current_app.logger.error('Error on  create_user_and_add_membership: %s', e)
                db.session.rollback()
                if re_enable_user:
                    User._update_user_in_kc(create_user_request)
                else:
                    KeycloakService.delete_user_by_username(create_user_request.user_name)
                users.append(User._get_error_dict(username, Error.FAILED_ADDING_USER_ERROR))
                continue

        return {'users': users}

    @staticmethod
    def _update_user_in_kc(create_user_request):
        update_user_request = KeycloakUser()
        update_user_request.user_name = create_user_request.user_name
        update_user_request.enabled = False
        KeycloakService.update_user(update_user_request)

    @staticmethod
    def _validate_and_throw_exception(memberships, org_id, single_mode):
        if single_mode:  # make sure no bulk operation and only owner is created using if no auth
            if len(memberships) > 1 or memberships[0].get('membershipType') not in [ADMIN, COORDINATOR]:
                raise BusinessException(Error.INVALID_USER_CREDENTIALS, None)
        else:
            check_auth(org_id=org_id, one_of_roles=(COORDINATOR, ADMIN, STAFF))
        # check if anonymous org ;these actions cannot be performed on normal orgs
        org = OrgModel.find_by_org_id(org_id)
        if not org or org.access_type != AccessType.ANONYMOUS.value:
            raise BusinessException(Error.INVALID_INPUT, None)

    @staticmethod
    def _create_new_user_and_membership(db_username, kc_user, membership, org_id):
        user_model: UserModel = UserModel(username=db_username,
                                          is_terms_of_use_accepted=False, status=Status.ACTIVE.value,
                                          type=Role.ANONYMOUS_USER.name,
                                          email=membership.get('email', None),
                                          firstname=kc_user.first_name, lastname=kc_user.last_name,
                                          login_source=LoginSource.BCROS.value)
        user_model.flush()
        membership_model = MembershipModel(org_id=org_id, user_id=user_model.id,
                                           membership_type_code=membership['membershipType'],
                                           membership_type_status=Status.ACTIVE.value)

        membership_model.flush()
        name = {'first_name': user_model.firstname, 'last_name': user_model.lastname}
        ActivityLogPublisher.publish_activity(Activity(org_id, ActivityAction.APPROVE_TEAM_MEMBER.value,
                                                       name=json.dumps(name),
                                                       value=membership['membershipType'],
                                                       id=user_model.id))
        return user_model

    @staticmethod
    def delete_otp_for_user(user_name, origin_url: str = None):
        """Reset the OTP of the user."""
        # TODO - handle when the multiple teams implemented for bceid..
        user = UserModel.find_by_username(user_name)
        membership = MembershipModel.find_membership_by_userid(user.id)
        org_id = membership.org_id
        check_auth(org_id=org_id, one_of_roles=(ADMIN, COORDINATOR, STAFF))
        try:
            KeycloakService.reset_otp(str(user.keycloak_guid))
            User.send_otp_authenticator_reset_notification(user.email, origin_url, org_id)
        except HTTPError as err:
            current_app.logger.error('update_user in keycloak failed %s', err)
            raise BusinessException(Error.UNDEFINED_ERROR, err) from err

    @staticmethod
    def send_otp_authenticator_reset_notification(recipient_email, origin_url, org_id):
        """Send Authenticator reset notification to the user."""
        current_app.logger.debug('<send_otp_authenticator_reset_notification')
        app_url = f"{origin_url}/{current_app.config.get('AUTH_WEB_TOKEN_CONFIRM_PATH')}"
        context_path = 'signin/bceid'
        login_url = f'{app_url}/{context_path}'
        data = {
            'accountId': org_id,
            'emailAddresses': recipient_email,
            'contextUrl': login_url
        }
        try:
            publish_to_mailer(QueueMessageTypes.OTP_RESET.value, data=data)
            current_app.logger.debug('<send_otp_authenticator_reset_notification')
            ActivityLogPublisher.publish_activity(Activity(org_id, ActivityAction.RESET_2FA.value,
                                                           name=recipient_email))
        except Exception as e:  # noqa=B901
            current_app.logger.error('<send_otp_authenticator_reset_notification failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None) from e

    @staticmethod
    def reset_password_for_anon_user(user_info: dict, user_name):
        """Reset the password of the user."""
        user = UserModel.find_by_username(user_name)
        membership = MembershipModel.find_membership_by_userid(user.id)
        org_id = membership.org_id
        org = OrgModel.find_by_org_id(org_id)
        if not org or org.access_type != AccessType.ANONYMOUS.value:
            raise BusinessException(Error.INVALID_INPUT, None)

        check_auth(org_id=org_id, one_of_roles=(ADMIN, STAFF))
        update_user_request = KeycloakUser()
        update_user_request.user_name = user_name.replace(IdpHint.BCROS.value + '/', '')
        update_user_request.password = user_info['password']
        update_user_request.update_password_on_login()

        try:
            kc_user = KeycloakService.update_user(update_user_request)
        except HTTPError as err:
            current_app.logger.error('update_user in keycloak failed %s', err)
            raise BusinessException(Error.UNDEFINED_ERROR, err) from err
        return kc_user

    @staticmethod
    @user_context
    def delete_anonymous_user(user_name, **kwargs):
        """
        Delete User Profile.

        1) check if the token user is admin/owner of the current user
        2) disable the user from kc
        3) set user status as INACTIVE
        4) set membership as inactive
        """
        user_from_context: UserContext = kwargs['user_context']
        admin_user: UserModel = UserModel.find_by_jwt_token()

        if not admin_user:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if admin_user.status == UserStatus.INACTIVE.value:
            raise BusinessException(Error.DELETE_FAILED_INACTIVE_USER, None)
        # handle validations.
        user = UserModel.find_by_username(user_name)
        membership = MembershipModel.find_membership_by_userid(user.id)
        org_id = membership.org_id
        is_valid_action = False

        # admin/owner deleteion
        admin_user_membership = MembershipModel.find_membership_by_user_and_org(admin_user.id, org_id)
        if admin_user_membership.membership_type_code in [ADMIN]:
            is_valid_action = True
        # staff admin deleteion
        is_staff_admin = Role.STAFF_CREATE_ACCOUNTS.value in user_from_context.token_info
        if is_staff_admin:
            is_valid_action = True
        # self deletion
        if user.keycloak_guid == admin_user.keycloak_guid:
            is_valid_action = True

        # is the only owner getting deleted
        if is_valid_action and membership.membership_type_code == ADMIN:
            count_of_owners = MembershipModel.get_count_active_owner_org_id(org_id)
            if count_of_owners == 1:
                is_valid_action = False
        if not is_valid_action:
            raise BusinessException(Error.INVALID_USER_CREDENTIALS, None)
        user.is_terms_of_use_accepted = False
        user.status = UserStatus.INACTIVE.value
        user.save()
        membership.status = Status.INACTIVE.value
        membership.save()
        update_user_request = KeycloakUser()
        update_user_request.user_name = user_name.replace(IdpHint.BCROS.value + '/', '')
        update_user_request.enabled = False
        KeycloakService.update_user(update_user_request)

    @staticmethod
    def _create_kc_user(membership):
        create_user_request = KeycloakUser()
        create_user_request.first_name = membership['username']
        create_user_request.user_name = membership['username']
        create_user_request.password = membership['password']
        create_user_request.enabled = True
        create_user_request.attributes = {'access_type': AccessType.ANONYMOUS.value}
        return create_user_request

    @classmethod
    @user_context
    def save_from_jwt_token(cls, request_json: Dict = None, **kwargs):
        """Save user to database (create/update)."""
        current_app.logger.debug('save_from_jwt_token')
        user_from_context: UserContext = kwargs['user_context']
        if not user_from_context.token_info:
            return None
        request_json = {} if not request_json else request_json

        is_anonymous_user = user_from_context.token_info.get('accessType', None) == AccessType.ANONYMOUS.value
        if is_anonymous_user:
            existing_user = UserModel.find_by_username(user_from_context.user_name)
        else:
            existing_user = UserModel.find_by_jwt_idp_userid()

        first_name, last_name = User._get_names(existing_user, request_json)

        if existing_user is None:
            user_model = UserModel.create_from_jwt_token(first_name, last_name)
        else:
            user_model = UserModel.update_from_jwt_token(existing_user, first_name, last_name,
                                                         is_login=request_json.get('isLogin', False))

        if not user_model:
            return None

        # If terms accepted, double check if there is a new TOS in place. If so, update the flag to false.
        if user_model.is_terms_of_use_accepted:
            document_type = DocumentType.TERMS_OF_USE_DIRECTOR_SEARCH.value if is_anonymous_user \
                else DocumentType.TERMS_OF_USE.value
            # get the digit version of the terms of service..ie d1 gives 1 ; d2 gives 2..for proper comparison
            latest_version = util.digitify(DocumentService.find_latest_version_by_type(document_type))
            current_version = util.digitify(user_model.terms_of_use_accepted_version)
            if latest_version > current_version:
                user_model.is_terms_of_use_accepted = False

        user = User(user_model)
        return user

    @staticmethod
    @user_context
    def _get_names(existing_user, request_json, **kwargs):
        # For BCeID, IDIM doesn't want to use the names from token
        user_from_context: UserContext = kwargs['user_context']
        if user_from_context.login_source == LoginSource.BCEID.value:
            first_name: str = request_json.get('firstName', existing_user.firstname) if existing_user \
                else request_json.get('firstName', None)
            last_name: str = request_json.get('lastName', existing_user.lastname) if existing_user \
                else request_json.get('lastName', None)
        else:
            first_name: str = user_from_context.first_name
            last_name: str = user_from_context.last_name
        return first_name, last_name

    @staticmethod
    def get_contacts():
        """Get the contact associated with this user."""
        current_app.logger.debug('get_contact')
        user = UserModel.find_by_jwt_token()
        if user is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        collection = []
        for contact_link in user.contacts:
            collection.append(ContactService(contact_link.contact).as_dict())
        return {'contacts': collection}

    @staticmethod
    def _get_error_dict(username, error):
        return {'username': username, 'http_status': error.value[1],
                'error': error.value[0]}

    @staticmethod
    def add_contact(contact_info: dict, throw_error_for_duplicates: bool = True):
        """Add contact information for an existing user."""
        current_app.logger.debug('add_contact')
        user = UserModel.find_by_jwt_token()
        if user is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # check for existing contact (we only want one contact per user)
        contact_link = ContactLinkModel.find_by_user_id(user.id)
        if contact_link is not None:
            if not throw_error_for_duplicates:
                # TODO may be throw whole object
                return None
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        contact = ContactModel(**camelback2snake(contact_info))
        contact = contact.flush()

        contact_link = ContactLinkModel()
        contact_link.user = user
        contact_link.contact = contact
        contact_link.save()

        return ContactService(contact)

    @staticmethod
    def update_contact(contact_info: dict):
        """Update a contact for an existing user."""
        current_app.logger.debug('update_contact')
        user = UserModel.find_by_jwt_token()
        if user is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # find the contact link for this user
        contact_link = ContactLinkModel.find_by_user_id(user.id)

        # now find the contact for the link
        if contact_link is None or contact_link.contact is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        contact = contact_link.contact
        contact.update_from_dict(**camelback2snake(contact_info))
        contact = contact.save()

        # return the updated contact
        return ContactService(contact)

    @staticmethod
    @user_context
    def update_terms_of_use(is_terms_accepted, terms_of_use_version, **kwargs):
        """Update terms of use for an existing user."""
        current_app.logger.debug('update_terms_of_use')
        user_from_context: UserContext = kwargs['user_context']
        if user_from_context.token_info is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        user = UserModel.update_terms_of_use(is_terms_accepted, terms_of_use_version)
        return User(user)

    @staticmethod
    def delete_contact():
        """Delete the contact for an existing user."""
        current_app.logger.info('delete_contact')
        user = UserModel.find_by_jwt_token()
        if not user or not user.contacts:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        deleted_contact = User.__delete_contact(user)

        if deleted_contact:
            return ContactService(deleted_contact)
        return None

    @staticmethod
    def __delete_contact(user):
        # unlink the user from its contact
        contact_link = ContactLinkModel.find_by_user_id(user.id)
        if contact_link:
            del contact_link.user
            contact_link = contact_link.flush()
            contact_link.commit()
            # clean up any orphaned contacts and links
            if not contact_link.has_links():
                contact = contact_link.contact
                contact_link.delete()
                contact.delete()
                return contact
        return None

    @staticmethod
    def find_users(first_name='', last_name='', email=''):
        """Return a list of users matching either the given username or the given email."""
        return UserModel.find_users(first_name=first_name, last_name=last_name, email=email)

    @classmethod
    @user_context
    def find_by_jwt_token(cls, **kwargs):
        """Find user from database by user token."""
        user_from_context: UserContext = kwargs['user_context']
        if not user_from_context.token_info:
            return None

        user_model = UserModel.find_by_jwt_token()

        if not user_model:
            if kwargs.get('silent_mode', False):
                return None
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        is_anonymous_user = user_from_context.token_info.get('accessType', None) == AccessType.ANONYMOUS.value
        is_govm_user = user_from_context.login_source == LoginSource.STAFF.value
        # If terms accepted , double check if there is a new TOS in place. If so, update the flag to false.
        if user_model.is_terms_of_use_accepted:
            if is_anonymous_user:
                document_type = DocumentType.TERMS_OF_USE_DIRECTOR_SEARCH.value
            elif is_govm_user:
                document_type = DocumentType.TERMS_OF_USE_GOVM.value
            else:
                document_type = DocumentType.TERMS_OF_USE.value
            # get the digit version of the terms of service..ie d1 gives 1 ; d2 gives 2..for proper comparison
            latest_version = util.digitify(DocumentService.find_latest_version_by_type(document_type))
            current_version = util.digitify(user_model.terms_of_use_accepted_version)
            if latest_version > current_version:
                user_model.is_terms_of_use_accepted = False

        return User(user_model)

    @classmethod
    def find_by_username(cls, username: str = None):
        """Find user by provided username."""
        if not username:
            return None

        # find locally
        user_model = UserModel.find_by_username(username)

        if not user_model:
            return None

        return User(user_model)

    @staticmethod
    def get_admins_for_membership(membership_id, status=Status.ACTIVE.value):
        """Get admins for a membership's org."""
        membership = MembershipModel.find_membership_by_id(membership_id)
        org_id = membership.org_id

        return UserModel.find_users_by_org_id_by_status_by_roles(org_id, CLIENT_ADMIN_ROLES, status)

    @staticmethod
    def get_admin_emails_for_org(org_id: int, status=Status.ACTIVE.value):
        """Get admin emails for an org."""
        admin_list = UserModel.find_users_by_org_id_by_status_by_roles(org_id, CLIENT_ADMIN_ROLES, status)
        return ','.join([str(x.contacts[0].contact.email) for x in admin_list if x.contacts])

    @staticmethod
    def delete_user():
        """Delete User Profile.

        Does the following
        1) Find the user using token
        2) Find all org membership for the user
        3) Check if the current user is the only owner for any org - If yes, deny the action
        4) Mark the membership as inactive on all orgs for the user
        5) Delete the contact information for the user and the accepted terms of service
        6) Mark the user record as inactive
        """
        current_app.logger.debug('<delete_user')

        user: UserModel = UserModel.find_by_jwt_token()
        if not user:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if user.status == UserStatus.INACTIVE.value:
            raise BusinessException(Error.DELETE_FAILED_INACTIVE_USER, None)

        user_orgs: List[OrgModel] = MembershipModel.find_orgs_for_user(user.id)

        current_app.logger.info(f'Found {len(user_orgs or [])} orgs for the user')

        if user_orgs:
            for org in user_orgs:
                current_app.logger.debug(f'Org : {org.name},  Status : {org.status_code}')
                if org.status_code == Status.ACTIVE.name:
                    User.__remove_org_membership(org, user.id)

        # Delete contact
        User.__delete_contact(user=user)

        # Set the user status as inactive
        user.status = UserStatus.INACTIVE.value

        # Remove accepted terms
        user.terms_of_use_accepted_version = None
        user.terms_of_use_version = None
        user.is_terms_of_use_accepted = False

        user.save()

        # Remove user from account_holders group
        KeycloakService.remove_from_account_holders_group(user.keycloak_guid)

        current_app.logger.debug('<delete_user')

    @staticmethod
    def __remove_org_membership(org, user_id):
        is_user_an_owner: bool = False
        org_has_other_owners: bool = False
        user_membership: MembershipModel = None
        for member in MembershipModel.find_members_by_org_id(org.id):
            if member.user_id == user_id:
                user_membership = member
                if member.membership_type_code == ADMIN:
                    is_user_an_owner = True
            elif member.membership_type_code == ADMIN:
                org_has_other_owners = True
        current_app.logger.info(
            f'Org :{org.name} --> User Owner : {is_user_an_owner},Has other owners :{org_has_other_owners}')
        if is_user_an_owner and not org_has_other_owners:
            current_app.logger.info(f'Affiliated entities : {len(org.affiliated_entities)}')
            if len(org.affiliated_entities) == 0:
                org.status_code = OrgStatus.INACTIVE.value
                org.flush()
            else:
                # Roll back the transaction as there could be situation where a change in one org
                # membership is flushed, but the next one fails. In this case roll back whole transaction
                org.rollback()
                raise BusinessException(Error.DELETE_FAILED_ONLY_OWNER, None)
        else:
            user_membership.status = Status.INACTIVE.value
            user_membership.flush()

    @staticmethod
    @user_context
    def is_context_user_staff(**kwargs):
        """Check if user in user context has is a staff."""
        user_from_context: UserContext = kwargs['user_context']
        return user_from_context.is_staff()

    @staticmethod
    def is_user_admin_or_coordinator(user, org_id: int) -> bool:
        """Check if user(userservice wrapper) provided is admin or coordinator for the given org id."""
        current_user_membership: MembershipModel = \
            MembershipModel.find_membership_by_user_and_org(user_id=user.identifier, org_id=org_id)

        if current_user_membership is None:
            return False

        if current_user_membership.status != Status.ACTIVE.value:
            return False

        return current_user_membership.membership_type_code in CLIENT_ADMIN_ROLES

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
from typing import List

from flask import current_app
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import User as UserModel
from auth_api.schemas import UserSchema
from auth_api.utils.roles import CLIENT_ADMIN_ROLES, OWNER, OrgStatus, Status, UserStatus
from auth_api.utils.util import camelback2snake

from .contact import Contact as ContactService


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class User:  # pylint: disable=too-many-instance-attributes
    """Manages all aspects of the User Entity.

    This manages storing the User in the cache,
    ensuring that the local cache is up to date,
    submitting changes back to all storage systems as needed.
    """

    def __init__(self, model):
        """Return a User Service object."""
        self._model = model

    @property
    def identifier(self):
        """Return the identifier for this user."""
        return self._model.id

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the User as a python dict.

        None fields are not included in the dict.
        """
        user_schema = UserSchema()
        obj = user_schema.dump(self._model, many=False)
        return obj

    @classmethod
    def save_from_jwt_token(cls, token: dict = None):
        """Save user to database (create/update)."""
        current_app.logger.debug('save_from_jwt_token')
        if not token:
            return None

        existing_user = UserModel.find_by_jwt_token(token)
        if existing_user is None:
            user_model = UserModel.create_from_jwt_token(token)
        else:
            user_model = UserModel.update_from_jwt_token(token, existing_user)

        if not user_model:
            return None

        user = User(user_model)
        return user

    @staticmethod
    def get_contacts(token):
        """Get the contact associated with this user."""
        current_app.logger.debug('get_contact')
        user = UserModel.find_by_jwt_token(token)
        if user is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        collection = []
        for contact_link in user.contacts:
            collection.append(ContactService(contact_link.contact).as_dict())
        return {'contacts': collection}

    @staticmethod
    def add_contact(token, contact_info: dict):
        """Add or update contact information for an existing user."""
        current_app.logger.debug('add_contact')
        user = UserModel.find_by_jwt_token(token)
        if user is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # check for existing contact (we only want one contact per user)
        contact_link = ContactLinkModel.find_by_user_id(user.id)
        if contact_link is not None:
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        contact = ContactModel(**camelback2snake(contact_info))
        contact.commit()

        contact_link = ContactLinkModel()
        contact_link.user = user
        contact_link.contact = contact
        contact_link.commit()

        return ContactService(contact)

    @staticmethod
    def update_contact(token, contact_info: dict):
        """Update a contact for an existing user."""
        current_app.logger.debug('update_contact')
        user = UserModel.find_by_jwt_token(token)
        if user is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # find the contact link for this user
        contact_link = ContactLinkModel.find_by_user_id(user.id)

        # now find the contact for the link
        if contact_link is None or contact_link.contact is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        contact = contact_link.contact
        contact.update_from_dict(**camelback2snake(contact_info))
        contact = contact.flush()
        contact.commit()

        # return the updated contact
        return ContactService(contact)

    @staticmethod
    def update_terms_of_use(token, is_terms_accepted, terms_of_use_version):
        """Update terms of use for an existing user."""
        current_app.logger.debug('update_terms_of_use')
        if token is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        user = UserModel.update_terms_of_use(token, is_terms_accepted, terms_of_use_version)
        return User(user)

    @staticmethod
    def delete_contact(token):
        """Delete the contact for an existing user."""
        current_app.logger.info('delete_contact')
        user = UserModel.find_by_jwt_token(token)
        if not user or not user.contacts:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        deleted_contact = User.__delete_contact(user)

        return ContactService(deleted_contact)

    @staticmethod
    def __delete_contact(user):
        # unlink the user from its contact
        contact_link = ContactLinkModel.find_by_user_id(user.id)
        if contact_link:
            del contact_link.user
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
    def find_by_jwt_token(cls, token: dict = None):
        """Find user from database by user token."""
        if not token:
            return None

        user = UserModel.find_by_jwt_token(token)

        if not user:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        return User(user)

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
        """Get admins for an org."""
        membership = MembershipModel.find_membership_by_id(membership_id)
        org_id = membership.org_id

        return UserModel.find_users_by_org_id_by_status_by_roles(org_id, CLIENT_ADMIN_ROLES, status)

    @staticmethod
    def delete_user(token):
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

        user: UserModel = UserModel.find_by_jwt_token(token)
        if not user:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if user.status == UserStatus.INACTIVE.value:
            raise BusinessException(Error.DELETE_FAILED_INACTIVE_USER, None)

        user_orgs: List[OrgModel] = MembershipModel.find_orgs_for_user(user.id)

        current_app.logger.info('Found {} orgs for the user'.format(len(user_orgs) if user_orgs else 0))

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
        current_app.logger.debug('<delete_user')

    @staticmethod
    def __remove_org_membership(org, user_id):
        is_user_an_owner: bool = False
        org_has_other_owners: bool = False
        user_membership: MembershipModel = None
        for member in MembershipModel.find_members_by_org_id(org.id):
            if member.user_id == user_id:
                user_membership = member
                if member.membership_type_code == OWNER:
                    is_user_an_owner = True
            elif member.membership_type_code == OWNER:
                org_has_other_owners = True
        current_app.logger.info(
            f'Org :{org.name} --> User Owner : {is_user_an_owner},Has other owners :{org_has_other_owners}')
        if is_user_an_owner and not org_has_other_owners:
            current_app.logger.info('Affiliated entities : {}'.format(len(org.affiliated_entities)))
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

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

from sbc_common_components.tracing.service_tracing import ServiceTracing

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import User as UserModel
from auth_api.schemas import UserSchema
from auth_api.utils.util import camelback2snake


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
    def add_contact(token, contact_info: dict):
        """Add or update contact information for an existing user."""
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

        return User(user)

    @staticmethod
    def update_contact(token, contact_info: dict):
        """Update a contact for an existing user."""
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

        # return the user with the updated contact
        return User(user)

    @staticmethod
    def delete_contact(token):
        """Delete the contact for an existing user."""
        user = UserModel.find_by_jwt_token(token)
        if not user or not user.contacts:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # unlink the user from its contact
        contact_link = ContactLinkModel.find_by_user_id(user.id)
        del contact_link.user
        contact_link.commit()

        # clean up any orphaned contacts and links
        if not contact_link.has_links():
            contact = contact_link.contact
            contact_link.delete()
            contact.delete()

        return User(user)

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

    def get_orgs(self):
        """Return the orgs associated with this user."""
        return {'orgs': self.as_dict()['orgs']}

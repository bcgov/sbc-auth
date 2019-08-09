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
from auth_api.models.contact import Contact as ContactModel
from auth_api.models.user import User as UserModel
from auth_api.models.user import UserSchema


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
            user_model = UserModel.update_from_jwt_token(token)

        if not user_model:
            return None

        user = User(user_model)
        return user

    @staticmethod
    def add_contact(username, contact_info: dict):
        """Add contact information for an existing user."""
        user = UserModel.find_by_username(username)
        if user is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        contact = ContactModel()
        contact.user_id = user.id
        contact.email = contact_info.get('emailAddress', None)
        contact.phone = contact_info.get('phoneNumber', None)
        contact.phone_extension = contact_info.get('extension', None)
        contact = contact.flush()
        contact.commit()

        return User(user)

    # @classmethod
    # def find_by_jwt_token(cls, token: dict = None):
    #     """Find user from database by user token."""
    #     if not token:
    #         return None

    #     user_dao = UserModel.find_by_jwt_token(token)

    #     if not user_dao:
    #         return None

    #     user = User()
    #     user._dao = user_dao  # pylint: disable=protected-access
    #     return user

    # @classmethod
    # def find_by_username(cls, username: str = None):
    #     """Given a username, this will return an Active User or None."""
    #     if not username:
    #         return None

    #     # find locally
    #     user_dao = UserModel.find_by_username(username)

    #     if not user_dao:
    #         return None

    #     user = User()
    #     user._dao = user_dao  # pylint: disable=protected-access
    #     return user

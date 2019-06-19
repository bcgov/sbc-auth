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

from datetime import date

from auth_api.models.users import Users as UsersModel
from sbc_common_components.tracing.service_tracing import ServiceTracing


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class User:  # pylint: disable=too-many-instance-attributes
    """Manages all aspects of the User Entity.

    This manages storing the User in the cache,
    ensuring that the local cache is up to date,
    submitting changes back to all storage systems as needed.
    """

    def __init__(self):
        """Return a User Service object."""
        self.__dao = None
        self._user_id: int = None
        self._username: str = None
        self._passwd: str = None
        self._firstname: str = None
        self._lastname: str = None
        self._display_name: str = None
        self._email: str = None
        self._user_source: str = None
        self._user_type_code: str = None
        self._sub: str = None
        self._iss: str = None
        self._creation_date: date = None

    @property
    def _dao(self):
        if not self.__dao:
            self.__dao = UsersModel()
        return self.__dao

    @_dao.setter
    def _dao(self, value):
        self.__dao = value
        self.user_id = self._dao.user_id
        self.username = self._dao.username
        self.passwd = self._dao.passwd
        self.firstname = self._dao.firstname
        self.lastname = self._dao.lastname
        self.display_name = self._dao.display_name
        self.email = self._dao.email
        self.user_source = self._dao.user_source
        self.user_type_code = self._dao.user_type_code
        self.sub = self._dao.sub
        self.iss = self._dao.iss
        self.creation_date = self._dao.creation_date

    @property
    def user_id(self):
        """Return the User id."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: int):
        """Set the User id."""
        self._user_id = value
        self._dao.user_id = value

    @property
    def username(self):
        """Return the User username."""
        return self._username

    @username.setter
    def username(self, value: str):
        """Set the User username."""
        self._username = value
        self._dao.username = value

    @property
    def passwd(self):
        """Return the User pasword (Passcode)."""
        return self._passwd

    @passwd.setter
    def passwd(self, value: str):
        """Set the User password (Passcode)."""
        self._passwd = value
        self._dao.passwd = value

    @property
    def firstname(self):
        """Return the User first name."""
        return self._firstname

    @firstname.setter
    def firstname(self, value: str):
        """Set the User first name."""
        self._firstname = value
        self._dao.firstname = value

    @property
    def lastname(self):
        """Return the User last name."""
        return self._lastname

    @lastname.setter
    def lastname(self, value: str):
        """Set the User last name."""
        self._lastname = value
        self._dao.lastname = value

    @property
    def display_name(self):
        """Return the User display name."""
        return self._display_name

    @display_name.setter
    def display_name(self, value: str):
        """Set the User display name."""
        self._display_name = value
        self._dao.display_name = value

    @property
    def email(self):
        """Return the User email."""
        return self._email

    @email.setter
    def email(self, value: str):
        """Set the User email."""
        self._email = value
        self._dao.email = value

    @property
    def user_source(self):
        """Return the User source."""
        return self._user_source

    @user_source.setter
    def user_source(self, value: str):
        """Set the User source."""
        self._user_source = value
        self._dao.user_source = value

    @property
    def user_type_code(self):
        """Return the User type code."""
        return self._user_type_code

    @user_type_code.setter
    def user_type_code(self, value: str):
        """Set the User type code."""
        self._user_type_code = value
        self._dao.user_type_code = value

    @property
    def iss(self):
        """Return the User iss."""
        return self._iss

    @iss.setter
    def iss(self, value: str):
        """Set the User iss."""
        self._iss = value
        self._dao.iss = value

    @property
    def sub(self):
        """Return the User sub."""
        return self._sub

    @sub.setter
    def sub(self, value: str):
        """Set the User sub."""
        self._sub = value
        self._dao.sub = value

    @property
    def creation_date(self):
        """Return the User Creation date."""
        return self._creation_date

    @creation_date.setter
    def creation_date(self, value: date):
        """Set the User Creation date."""
        self._creation_date = value
        self._dao.creation_date = value

    @ServiceTracing.disable_tracing
    def asdict(self):
        """Return the User as a python dict.

        None fields are not included in the dict.
        """
        d = {
            'user_id': self.user_id,
            'username': self.username,
            'passwd': self.passwd,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'display_name': self.display_name,
            'email': self.email,
            'user_source': self.user_source,
            'user_type_code': self.user_type_code,
            'sub': self.sub,
            'iss': self.iss,
            'creation_date': self.creation_date
        }
        return d

    def save(self):
        """Save the User information to the local cache."""
        self._dao.save()

    @classmethod
    def save_from_jwt_token(cls, token: dict = None):
        """Save user to database."""
        if not token:
            return None
        user_dao = UsersModel.create_from_jwt_token(token)

        if not user_dao:
            return None

        user = User()
        user._dao = user_dao  # pylint: disable=protected-access
        return user

    @classmethod
    def find_by_jwt_token(cls, token: dict = None):
        """Find user from database by user token."""
        if not token:
            return None

        user_dao = UsersModel.find_by_jwt_token(token)

        if not user_dao:
            return None

        user = User()
        user._dao = user_dao  # pylint: disable=protected-access
        return user

    @classmethod
    def find_by_username(cls, username: str = None):
        """Given a username, this will return an Active User or None."""
        if not username:
            return None

        # find locally
        user_dao = UsersModel.find_by_username(username)

        if not user_dao:
            return None

        user = User()
        user._dao = user_dao  # pylint: disable=protected-access
        return user

# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The User service.

This module manages the User Information.
"""

from datetime import datetime

from auth_api.exceptions import UserException
from auth_api.models import User as UserModel


class User():  # pylint: disable=too-many-instance-attributes
    """Manages all aspects of the User Entity.

    This manages storing the User in the cache,
    ensuring that the local cache is up to date,
    submitting changes back to all storage systems as needed.
    """

    def __init__(self):
        """Return a User Service object."""
        self.__dao = None
        self._username: str = None
        self._roles: str = None

    def __init__(self, username, roles):
        self.__dao = None
        self.username = username
        self.roles = roles

    def json(self):
        return {"username": self.username, "roles": self.roles}

    @property
    def _dao(self):
        if not self.__dao:
            self.__dao = UserModel()
        return self.__dao

    @_dao.setter
    def _dao(self, value):
        self.__dao = value
        self.username = self._dao.username
        self.roles = self._dao.roles

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
    def roles(self):
        """Return the User roles."""
        return self._roles

    @roles.setter
    def roles(self, value: str):
        """Set the User roles."""
        self._roles = value
        self._dao.roles = value

    def asdict(self):
        """Return the User as a python dict.

        None fields are not included in the dict.
        """
        d = {
            'username': self.username,
        }
        if self.roles:
            d['roles'] = self.roles
        return d

    def save(self):
        """Save the User information to the local cache."""
        self._dao.save()

    @classmethod
    def find_by_username(cls, username: str = None):
        """Given a username, this will return an Active User or None."""
        if not username:
            return None

        # find locally
        User_dao = None
        User_dao = UserModel.find_by_username(username)

        # TODO check if timestamp is valid in Colin
        if not User_dao:
            return None

        b = User()
        b._dao = User_dao  # pylint: disable=protected-access
        return b

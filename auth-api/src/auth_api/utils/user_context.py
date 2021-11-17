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
"""User Context to hold request scoped variables."""

import functools
from typing import Dict

from flask import g, request

# from auth_api.models import User as UserModel
from auth_api.utils.enums import LoginSource
from auth_api.utils.roles import Role


def _get_context():
    """Return User context."""
    return UserContext()


class UserContext:  # pylint: disable=too-many-instance-attributes
    """Object to hold request scoped user context."""

    def __init__(self):
        """Return a User Context object."""
        token_info: Dict = _get_token_info() or {}
        self._token_info = token_info
        self._user_name: str = token_info.get('username', token_info.get('preferred_username', None))
        self._first_name: str = token_info.get('firstname', None)
        self._last_name: str = token_info.get('lastname', None)
        self._bearer_token: str = _get_token()
        self._roles: list = token_info.get('realm_access', None).get('roles', []) if 'realm_access' in token_info \
            else []
        self._sub: str = token_info.get('sub', None)
        self._login_source: str = token_info.get('loginSource', None)
        self._name: str = f"{token_info.get('firstname', None)} {token_info.get('lastname', None)}"

    @property
    def user_name(self) -> str:
        """Return the user_name."""
        return self._user_name if self._user_name else None

    @property
    def first_name(self) -> str:
        """Return the user_first_name."""
        return self._first_name

    @property
    def last_name(self) -> str:
        """Return the user_last_name."""
        return self._last_name

    @property
    def bearer_token(self) -> str:
        """Return the bearer_token."""
        return self._bearer_token

    @property
    def roles(self) -> list:
        """Return the roles."""
        return self._roles

    @property
    def sub(self) -> str:
        """Return the subject."""
        return self._sub

    def has_role(self, role_name: str) -> bool:
        """Return True if the user has the role."""
        return role_name in self._roles

    def is_staff(self) -> bool:
        """Return True if the user is staff user."""
        return Role.STAFF.value in self._roles if self._roles else False

    def is_staff_admin(self) -> bool:
        """Return True if the user is staff user."""
        return Role.STAFF_CREATE_ACCOUNTS.value in self._roles if self._roles else False

    def is_system(self) -> bool:
        """Return True if the user is system user."""
        return Role.SYSTEM.value in self._roles if self._roles else False

    def is_bceid_user(self) -> bool:
        """Return True if the user is BCEID user."""
        return self._login_source == LoginSource.BCEID.value

    @property
    def name(self) -> str:
        """Return the name."""
        return self._name

    @property
    def token_info(self) -> Dict:
        """Return the name."""
        return self._token_info

    @property
    def account_id_claim(self) -> Dict:
        """Return the account id."""
        return _get_token_info().get('Account-Id', None)

    @property
    def account_id(self) -> Dict:
        """Return the account id."""
        account_id = _get_token_info().get('Account-Id', None)
        if not account_id:
            account_id = request.headers['Account-Id'] if request and 'Account-Id' in request.headers else None
        return account_id

    @property
    def login_source(self) -> str:
        """Return the login source."""
        return self._login_source


def user_context(function):
    """Add user context object as an argument to function."""

    @functools.wraps(function)
    def wrapper(*func_args, **func_kwargs):
        context = _get_context()
        func_kwargs['user_context'] = context
        return function(*func_args, **func_kwargs)

    return wrapper


def _get_token_info() -> Dict:
    return g.jwt_oidc_token_info if g and 'jwt_oidc_token_info' in g else {}


def _get_token() -> str:
    token: str = request.headers['Authorization'] if request and 'Authorization' in request.headers else None
    return token.replace('Bearer ', '') if token else None

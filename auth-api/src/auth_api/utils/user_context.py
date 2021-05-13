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
from typing import Dict, List

from flask import g, request
from auth_api.models import User as UserModel
from auth_api.utils.enums import LoginSource
from auth_api.utils.roles import Role


def _get_context():
    """Return User context."""
    return UserContext()


class UserContext:  # pylint: disable=too-many-instance-attributes
    """Object to hold request scoped user context."""

    def __init__(self):
        """Return a User Context object."""
        token_info: Dict = _get_token_info()
        user_model: UserModel = UserModel.find_by_jwt_token(token_info)
        self._user_id = None
        if user_model:
            self._user_id = user_model.id
        self._user_name: str = token_info.get('username', token_info.get('preferred_username', None))
        self._first_name: str = token_info.get('firstname', None)
        self._bearer_token: str = _get_token()
        self._roles: list = token_info.get('realm_access', None).get('roles', None) if 'realm_access' in token_info \
            else None
        self._sub: str = token_info.get('sub', None)
        self._login_source: str = token_info.get('loginSource', None)
        self._account_id: str = get_auth_account_id()
        self._name: str = '{} {}'.format(token_info.get('firstname', None), token_info.get('lastname', None))
        self._product_code: str = token_info.get('product_code', None)
        self._permission = _get_permission()

    @property
    def user_name(self) -> str:
        """Return the user_name."""
        return self._user_name.upper() if self._user_name else None

    @property
    def user_name_with_no_idp(self) -> str:
        """Return the user_name with no idp info."""
        user_name = self.user_name
        if user_name:
            login_source = self._login_source.upper()
            user_name = user_name.replace(f'@{login_source}', '').replace(f'{login_source}\\', '')
        return user_name

    @property
    def first_name(self) -> str:
        """Return the user_name."""
        return self._first_name

    @property
    def user_id(self) -> str:
        """Return the user_name."""
        return self._user_id

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

    @property
    def account_id(self) -> str:
        """Return the account_id."""
        return self._account_id

    @property
    def permission(self) -> List[str]:
        """Return the permission."""
        return self._permission

    @property
    def product_code(self) -> str:
        """Return the product_code."""
        return self._product_code

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


def user_context(function):
    """Add user context object as an argument to function."""

    @functools.wraps(function)
    def wrapper(*func_args, **func_kwargs):
        context = _get_context()
        func_kwargs['user'] = context
        return function(*func_args, **func_kwargs)

    return wrapper


def _get_token_info() -> Dict:
    return g.jwt_oidc_token_info if g and 'jwt_oidc_token_info' in g else {}


def _get_permission() -> Dict:
    return g.user_permission if g and 'user_permission' in g else []


def _get_token() -> str:
    token: str = request.headers['Authorization'] if request and 'Authorization' in request.headers else None
    return token.replace('Bearer ', '') if token else None


def get_auth_account_id() -> str:
    """Return account id from the header."""
    return request.headers['Account-Id'] if request and 'Account-Id' in request.headers else None

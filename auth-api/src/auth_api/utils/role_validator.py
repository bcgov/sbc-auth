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

"""Roles validator decorator.

A simple decorator to validate roles.
"""
from functools import wraps
from typing import Dict

from flask import g

from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException, Error


def validate_roles(**role_args):
    """Verify the roles .

    Args:
        allowed_roles [str,]: Comma separated list of any valid roles
        not_allowed_roles [str,]: Comma separated list of any invalid roles
    """

    def decorated(f):
        @wraps(f)
        @_jwt.requires_auth
        def wrapper(*args, **kwargs):
            token_info: Dict = _get_token_info() or {}
            user_roles: list = token_info.get('realm_access', None).get('roles', []) if 'realm_access' in token_info \
                else []
            allowed_roles = role_args.get('allowed_roles', [])
            not_allowed_roles = role_args.get('not_allowed_roles', [])
            if len(set(allowed_roles).intersection(user_roles)) < 1:
                raise BusinessException(Error.MISSING_ROLES, None)
            if len(set(not_allowed_roles).intersection(user_roles)) > 1:
                raise BusinessException(Error.MISSING_ROLES, None)
            return f(*args, **kwargs)

        return wrapper

    return decorated


def _get_token_info() -> Dict:
    return g.jwt_oidc_token_info if g and 'jwt_oidc_token_info' in g else {}

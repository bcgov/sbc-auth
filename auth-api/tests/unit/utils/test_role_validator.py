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

"""Tests to assure the Role validator."""
from unittest.mock import patch

import pytest

from auth_api.utils.auth import jwt as _jwt
from auth_api.utils.role_validator import validate_roles


@patch.object(_jwt, "requires_auth", side_effect=lambda f: f)
@pytest.mark.parametrize(
    "allowed_roles,not_allowed_roles",
    [
        (["role1"], [""]),  # just one allowed role
        (["role1", "role2"], [""]),  # one more additional role
        (["role1"], ["role3"]),  # one not allowed role which user doesnt have
    ],
)
def test_validate_roles_valid(jwt, monkeypatch, allowed_roles, not_allowed_roles):
    """Assert that valid roles yields proper response."""
    token = {
        "realm_access": {"roles": ["role1"]},
    }
    monkeypatch.setattr("auth_api.utils.role_validator._get_token_info", lambda: token)

    @validate_roles(allowed_roles=allowed_roles, not_allowed_roles=not_allowed_roles)
    def decorated(x):
        return x

    assert decorated(1) == 1


@patch.object(_jwt, "requires_auth", side_effect=lambda f: f)
@pytest.mark.parametrize(
    "allowed_roles,not_allowed_roles",
    [
        ([""], [""]),  # no allowed role
        (["role1"], ["role1"]),  # allowed role ;but not_allowed_roles prohibits access
        ([""], ["role1"]),  # not_allowed_roles prohibits access
    ],
)
def test_validate_roles_invalid(jwt, monkeypatch, allowed_roles, not_allowed_roles):
    """Assert that invalid roles yields error response."""
    token = {"realm_access": {"roles": ["role1"]}}
    monkeypatch.setattr("auth_api.utils.role_validator._get_token_info", lambda: token)

    @validate_roles(allowed_roles=allowed_roles, not_allowed_roles=not_allowed_roles)
    def decorated(x):
        return x

    with pytest.raises(Exception) as excinfo:
        decorated(1)
        assert excinfo.code == 401

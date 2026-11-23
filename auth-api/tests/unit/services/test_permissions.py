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

"""Tests to verify the Permissions Service.

Test-Suite to ensure that the Permissions Service is working as expected.
"""

from unittest.mock import patch

import pytest

from auth_api.models import OrgType as OrgTypeModel
from auth_api.services import Permissions as PermissionService
from auth_api.services import User as UserService
from auth_api.utils.cache import cache
from auth_api.utils.enums import OrgType
from tests.utilities.factory_scenarios import TestJwtClaims, TestUserInfo
from tests.utilities.factory_utils import (
    factory_membership_model,
    factory_org_model,
    factory_user_model,
    patch_token_info,
)


def test_build_all_permission_cache(session):  # pylint: disable=unused-argument
    """Assert that building cache works."""
    PermissionService.build_all_permission_cache()
    assert cache is not None
    assert cache.get((None, "ADMIN")) is not None


def test_get_permissions_for_membership_cache_miss(session):  # pylint: disable=unused-argument
    """Assert the cache miss and hit."""
    PermissionService.build_all_permission_cache()
    with patch("auth_api.models.Permissions.get_permissions_by_membership") as method:
        PermissionService.get_permissions_for_membership("ACTIVE", "ADMIN")
        assert not method.called, "Should Not miss the Cache"
        PermissionService.get_permissions_for_membership("invalid", "invalid")
        assert method.called, "Should miss the Cache"


@pytest.mark.parametrize(
    "membership_type, claims, org_type",
    [
        ("SBC_FIN_STAFF", TestJwtClaims.sbc_finance_staff_role, OrgType.SBC_FIN_STAFF.value),
        ("EXTERNAL_STAFF", TestJwtClaims.external_staff_readonly_role, OrgType.MAXIMUS_STAFF.value),
    ],
)
def test_get_permissions_for_membership_has_no_duplicates(
    session, monkeypatch, disable_org_update_listener, membership_type, claims, org_type
):  # pylint: disable=unused-argument
    """Assert permissions are not duplicated on cache hit or miss when including all permissions."""
    PermissionService.build_all_permission_cache()
    user = factory_user_model(
        user_info={**TestUserInfo.user1, "keycloak_guid": claims["sub"], "idp_userid": claims["idp_userid"]}
    )
    org = factory_org_model(user_id=user.id)
    org.org_type = OrgTypeModel.get_type_for_code(org_type)
    org.save()
    factory_membership_model(user.id, org.id, member_type="USER")
    patch_token_info(claims, monkeypatch)

    actions = PermissionService.get_permissions_for_membership(
        None, membership_type, UserService(user), include_all_permissions=True
    )

    assert len(actions) == len(set(actions))

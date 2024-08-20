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

from auth_api.services import Permissions as PermissionService
from auth_api.utils.cache import cache


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

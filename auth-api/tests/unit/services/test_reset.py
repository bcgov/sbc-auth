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

"""Tests to verify the reset data Service.

Test-Suite to ensure that the reset data Service is working as expected.
"""

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.services import Membership as MembershipService
from auth_api.services import Org as OrgService
from auth_api.services import ResetTestData as ResetDataService
from auth_api.services import User as UserService
from auth_api.services.entity import Entity as EntityService
from tests.utilities.factory_scenarios import TestJwtClaims, TestUserInfo
from tests.utilities.factory_utils import (
    factory_entity_model, factory_membership_model, factory_org_model, factory_user_model)


def test_reset(session, auth_mock):  # pylint: disable=unused-argument
    """Assert that can be reset data by the provided token."""
    user_with_token = TestUserInfo.user_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.tester_role['sub']
    user = factory_user_model(user_info=user_with_token)
    org = factory_org_model(user_id=user.id)
    factory_membership_model(user.id, org.id)
    entity = factory_entity_model(user_id=user.id)

    ResetDataService.reset(TestJwtClaims.tester_role)

    with pytest.raises(BusinessException) as exception:
        UserService.find_by_jwt_token(user_with_token)
    assert exception.value.code == Error.DATA_NOT_FOUND.name

    found_org = OrgService.find_by_org_id(org.id)
    assert found_org is None

    found_entity = EntityService.find_by_entity_id(entity.id)
    assert found_entity is None

    found_memeber = MembershipService.get_members_for_org(org.id)
    assert found_memeber is None


def test_reset_user_notexists(session, auth_mock):  # pylint: disable=unused-argument
    """Assert that can not be reset data by the provided token not exists in database."""
    response = ResetDataService.reset(TestJwtClaims.tester_role)
    assert response is None

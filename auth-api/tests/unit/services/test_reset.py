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
from auth_api.services.keycloak import KeycloakService
from tests.utilities.factory_scenarios import KeycloakScenario, TestEntityInfo, TestJwtClaims, TestUserInfo
from tests.utilities.factory_utils import (
    factory_entity_model, factory_membership_model, factory_org_model, factory_user_model, patch_token_info)


def test_reset(session, auth_mock, monkeypatch):  # pylint: disable=unused-argument
    """Assert that can be reset data by the provided token."""
    user_with_token = TestUserInfo.user_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.tester_role['sub']
    user_with_token['idp_userid'] = TestJwtClaims.tester_role['idp_userid']
    user = factory_user_model(user_info=user_with_token)
    org = factory_org_model(user_id=user.id)
    factory_membership_model(user.id, org.id)
    entity = factory_entity_model(user_id=user.id)

    patch_token_info(TestJwtClaims.tester_role, monkeypatch)
    ResetDataService.reset()

    with pytest.raises(BusinessException) as exception:
        patch_token_info(user_with_token, monkeypatch)
        UserService.find_by_jwt_token()
    assert exception.value.code == Error.DATA_NOT_FOUND.name

    found_org = OrgService.find_by_org_id(org.id)
    assert found_org is None

    found_entity = EntityService.find_by_entity_id(entity.id)
    assert found_entity is not None
    dictionary = found_entity.as_dict()
    assert dictionary['business_identifier'] == TestEntityInfo.entity1['businessIdentifier']
    assert not dictionary['pass_code_claimed']

    found_memeber = MembershipService.get_members_for_org(org.id)
    assert found_memeber is None


def test_reset_user_notexists(session, auth_mock, monkeypatch):  # pylint: disable=unused-argument
    """Assert that can not be reset data by the provided token not exists in database."""
    patch_token_info(TestJwtClaims.tester_role, monkeypatch)
    response = ResetDataService.reset()
    assert response is None


def test_reset_user_without_tester_role(session, auth_mock, monkeypatch):  # pylint: disable=unused-argument
    """Assert that can not be reset data by the user doesn't have tester role."""
    user_with_token = TestUserInfo.user_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.tester_role['sub']
    user = factory_user_model(user_info=user_with_token)
    org = factory_org_model(user_id=user.id)

    patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
    response = ResetDataService.reset()
    assert response is None

    found_org = OrgService.find_by_org_id(org.id)
    assert found_org is not None


def test_reset_bceid_user(session, auth_mock, monkeypatch):  # pylint: disable=unused-argument
    """Assert that reset data from a bceid user."""
    keycloak_service = KeycloakService()
    patch_token_info(TestJwtClaims.tester_bceid_role, monkeypatch)

    request = KeycloakScenario.create_user_by_user_info(TestJwtClaims.tester_bceid_role)
    keycloak_service.add_user(request, return_if_exists=True)
    user = keycloak_service.get_user_by_username(request.user_name)
    assert user is not None
    user_id = user.id
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = user_id
    user_with_token['idp_userid'] = user_id
    user = factory_user_model(user_info=user_with_token)
    org = factory_org_model(user_id=user.id)

    patch_token_info(TestJwtClaims.get_test_user(user_id, 'BCEID'), monkeypatch)
    response = ResetDataService.reset()
    assert response is None

    found_org = OrgService.find_by_org_id(org.id)
    assert found_org is None

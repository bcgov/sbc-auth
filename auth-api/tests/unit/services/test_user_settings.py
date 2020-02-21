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

"""Tests to verify the User Service.

Test-Suite to ensure that the User Service is working as expected.
"""

from auth_api.services import Org as OrgService
from auth_api.services import User as UserService
from auth_api.services import UserSettings as UserSettingsService
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import factory_user_model


def test_user_settings(session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a contact can not be deleted if contact link exists."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.edit_role['sub']
    user_model = factory_user_model(user_info=user_with_token)
    user = UserService(user_model)

    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.identifier)
    org_dictionary = org.as_dict()
    org_id = org_dictionary['id']

    usersettings = UserSettingsService.fetch_user_settings(user.identifier)
    assert usersettings is not None
    org = [x for x in usersettings if x.type == 'ACCOUNT']
    assert len(usersettings) == 3
    assert org[0].label == TestOrgInfo.org1['name']
    assert org[0].id == org_id

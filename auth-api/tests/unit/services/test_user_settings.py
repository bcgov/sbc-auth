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

import mock
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService
from auth_api.services import UserSettings as UserSettingsService
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import factory_user_model, patch_token_info
from tests.conftest import mock_token

@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
def test_user_settings(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that a contact can not be deleted if contact link exists."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_user_role['idp_userid']
    user_model = factory_user_model(user_info=user_with_token)
    user = UserService(user_model)

    patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.identifier)
    org_dictionary = org.as_dict()
    org_id = org_dictionary['id']

    usersettings = UserSettingsService.fetch_user_settings(user.identifier)
    assert usersettings is not None
    org = [x for x in usersettings if x.type == 'ACCOUNT']
    assert len(usersettings) == 3
    assert org[0].label == TestOrgInfo.org1['name']
    assert org[0].id == org_id
    assert org[0].additional_label == '', 'no additional label'

    # add an org with branch name and assert additonal label
    org = OrgService.create_org(TestOrgInfo.org_branch_name, user_id=user.identifier)
    org_with_branch_dictionary = org.as_dict()

    usersettings = UserSettingsService.fetch_user_settings(user.identifier)
    assert len(usersettings) == 4
    org = [x for x in usersettings if x.type == 'ACCOUNT' and x.label == org_with_branch_dictionary.get('name')]
    assert org[0].additional_label == org_with_branch_dictionary.get('branch_name'), 'additional label matches'

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

"""Tests to assure the users API end-point.

Test-Suite to ensure that the /users endpoint is working as expected.
"""
import copy

from auth_api import status as http_status
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.schemas import utils as schema_utils
from auth_api.services import Org as OrgService
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import (
    factory_auth_header, factory_contact_model, factory_user_model, patch_token_info)


def test_get_user_settings(client, jwt, session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that get works and adhere to schema."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.commit()
    kc_id = user_model.keycloak_guid

    claims = copy.deepcopy(TestJwtClaims.updated_test.value)
    claims['sub'] = str(kc_id)
    patch_token_info(claims, monkeypatch)

    OrgService.create_org(TestOrgInfo.org_branch_name, user_id=user_model.id)

    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f'/api/v1/users/{kc_id}/settings', headers=headers, content_type='application/json')
    item_list = rv.json
    account = next(obj for obj in item_list if obj['type'] == 'ACCOUNT')
    assert account['accountType'] == 'BASIC'
    assert account['additionalLabel'] == TestOrgInfo.org_branch_name.get('branchName')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(item_list, 'user_settings_response')[0]
    assert account['productSettings'] == f'/account/{account["id"]}/restricted-product'

    kc_id_no_user = TestUserInfo.user1.get('keycloak_guid')
    claims = copy.deepcopy(TestJwtClaims.updated_test.value)
    claims['sub'] = str(kc_id_no_user)
    patch_token_info(claims, monkeypatch)
    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f'/api/v1/users/{kc_id_no_user}/settings', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(item_list, 'user_settings_response')[0]
    item_list = rv.json
    account = next((obj for obj in item_list if obj['type'] == 'ACCOUNT'), None)
    assert account is None
    user_profile = next(obj for obj in item_list if obj['type'] == 'USER_PROFILE')
    assert '/userprofile' in user_profile.get('urlpath')

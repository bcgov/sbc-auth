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
from http import HTTPStatus
from unittest import mock

from auth_api.models import ContactLink as ContactLinkModel
from auth_api.schemas import utils as schema_utils
from auth_api.services import Org as OrgService
from tests.conftest import mock_token
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import (
    factory_auth_header,
    factory_contact_model,
    factory_user_model,
    patch_token_info,
)


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_get_user_settings(client, jwt, session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that get works and adhere to schema."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.save()
    kc_id = user_model.keycloak_guid

    claims = copy.deepcopy(TestJwtClaims.updated_test.value)
    claims["sub"] = str(kc_id)
    claims["idp_userid"] = str(user_model.idp_userid)
    patch_token_info(claims, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org_branch_name, user_id=user_model.id)
    org_dict = org.as_dict()
    org_id = org_dict["id"]

    # Test without org contact - mailingAddress should be None
    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f"/api/v1/users/{kc_id}/settings", headers=headers, content_type="application/json")
    item_list = rv.json
    account = next(obj for obj in item_list if obj["type"] == "ACCOUNT")
    assert account["accountType"] == "PREMIUM"
    assert account["additionalLabel"] == TestOrgInfo.org_branch_name.get("branchName")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(item_list, "user_settings_response")[0]
    assert account["productSettings"] == f"/account/{account['id']}/restricted-product"
    assert "mailingAddress" in account
    assert account["mailingAddress"] is None

    # Add org contact and test with mailingAddress
    org_contact = factory_contact_model()
    org_contact.city = "Victoria"
    org_contact.save()
    org_contact_link = ContactLinkModel()
    org_contact_link.contact = org_contact
    org_contact_link.org = org._model  # pylint:disable=protected-access
    org_contact_link.save()

    rv = client.get(f"/api/v1/users/{kc_id}/settings", headers=headers, content_type="application/json")
    item_list = rv.json
    account = next(obj for obj in item_list if obj["type"] == "ACCOUNT")
    assert account["id"] == org_id
    assert "mailingAddress" in account
    assert isinstance(account["mailingAddress"], dict)
    assert "city" in account["mailingAddress"]
    assert account["mailingAddress"]["city"] == "Victoria"

    kc_id_no_user = dict(TestUserInfo.user1).get("keycloak_guid")
    claims = copy.deepcopy(TestJwtClaims.updated_test.value)
    claims["sub"] = str(kc_id_no_user)
    patch_token_info(claims, monkeypatch)
    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f"/api/v1/users/{kc_id_no_user}/settings", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(item_list, "user_settings_response")[0]
    item_list = rv.json
    account = next((obj for obj in item_list if obj["type"] == "ACCOUNT"), None)
    assert account is None
    user_profile = next(obj for obj in item_list if obj["type"] == "USER_PROFILE")
    assert "/userprofile" in user_profile.get("urlpath")

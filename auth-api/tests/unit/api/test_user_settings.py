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
from tests.utilities.factory_utils import factory_auth_header, factory_contact_model, factory_user_model


def test_get_user_settings(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that get works and adhere to schema."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.commit()
    kc_id = user_model.keycloak_guid

    OrgService.create_org(TestOrgInfo.org1, user_id=user_model.id)

    claims = copy.deepcopy(TestJwtClaims.updated_test.value)
    claims['sub'] = str(kc_id)
    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f'/api/v1/users/{kc_id}/settings', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'user_settings_response')

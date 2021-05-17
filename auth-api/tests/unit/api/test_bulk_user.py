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
import json

from auth_api import status as http_status
from auth_api.services.keycloak import KeycloakService
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_auth_header, factory_invitation_anonymous

KEYCLOAK_SERVICE = KeycloakService()


def test_add_user_admin_valid(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org admin can create members."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_dir_search_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_anonymous),
                     headers=headers, content_type='application/json')


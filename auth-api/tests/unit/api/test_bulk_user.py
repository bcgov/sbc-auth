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

from tests.utilities.factory_scenarios import BulkUserTestScenario, TestJwtClaims, \
    TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import (
    factory_auth_header, factory_invitation_anonymous)

KEYCLOAK_SERVICE = KeycloakService()


def test_add_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_add_user_admin_valid_bcros(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org admin can create members."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_anonymous),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation_anonymous(org_id=org_id)),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    assert dictionary.get('token') is not None
    assert rv.status_code == http_status.HTTP_201_CREATED
    rv = client.post('/api/v1/users/bcros', data=json.dumps(TestUserInfo.user_anonymous_1),
                     headers={'invitation_token': dictionary.get('token')}, content_type='application/json')
    dictionary = json.loads(rv.data)

    headers = factory_auth_header(jwt=jwt,
                                  claims=TestJwtClaims.get_test_real_user(dictionary['users'][0]['keycloakGuid']))
    rv = client.post('/api/v1/bulk/users', headers=headers,
                     data=json.dumps(BulkUserTestScenario.get_bulk_user1_for_org(org_id)),
                     content_type='application/json')
    assert len(rv.json['users']) == 2

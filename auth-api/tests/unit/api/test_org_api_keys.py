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

"""Tests to verify the api keys endpoint.

Test-Suite to ensure that the /orgs/api-keys endpoint is working as expected.
"""

import json

from auth_api import status as http_status
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_auth_header


def test_create_api_keys(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that api keys can be generated."""
    # First create an account
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1), headers=headers,
                     content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert not rv.json.get('hasApiAccess')
    org_id = rv.json.get('id')

    # Create a system token and create an API key for this account.
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.post(f'/api/v1/orgs/{org_id}/api-keys', headers=headers, content_type='application/json',
                     data=json.dumps({
                         'environment': 'dev',
                         'keyName': 'TEST'
                     }))
    assert rv.json.get('apiKey')

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get(f'/api/v1/orgs/{org_id}', headers=headers, content_type='application/json')
    assert rv.json.get('hasApiAccess')


def test_list_api_keys(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that api keys can be listed."""
    # First create an account
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1), headers=headers,
                     content_type='application/json')
    org_id = rv.json.get('id')

    # Create a system token and create an API key for this account.
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.post(f'/api/v1/orgs/{org_id}/api-keys', headers=headers, content_type='application/json',
                     data=json.dumps({
                         'environment': 'dev',
                         'keyName': 'TEST'
                     }))

    rv = client.post(f'/api/v1/orgs/{org_id}/api-keys', headers=headers, content_type='application/json',
                     data=json.dumps({
                         'environment': 'dev',
                         'keyName': 'TEST 2'
                     }))

    rv = client.get(f'/api/v1/orgs/{org_id}/api-keys', headers=headers, content_type='application/json')
    assert rv.json['consumer']['consumerKey']


def test_revoke_api_key(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that api keys can be revoked."""
    # First create an account
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=user_headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1), headers=user_headers,
                     content_type='application/json')
    org_id = rv.json.get('id')

    # Create a system token and create an API key for this account.
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.post(f'/api/v1/orgs/{org_id}/api-keys', headers=headers, content_type='application/json',
                     data=json.dumps({
                         'environment': 'dev',
                         'keyName': 'TEST'
                     }))

    rv = client.get(f'/api/v1/orgs/{org_id}/api-keys', headers=headers, content_type='application/json')
    key = '7SmDGL4233wnp2dyXGSGGq7xutYlTzIN'  # from mock

    rv = client.delete(f'/api/v1/orgs/{org_id}/api-keys/{key}', headers=headers, content_type='application/json')
    assert rv.status_code == 200

    rv = client.delete(f'/api/v1/orgs/{org_id}/api-keys/{key}', headers=user_headers, content_type='application/json')
    assert rv.status_code == 200

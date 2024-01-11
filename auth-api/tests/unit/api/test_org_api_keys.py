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
import mock

from auth_api import status as http_status
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_auth_header
from tests.conftest import mock_token


@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
def test_create_api_keys(client, jwt, session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
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
    # Patch to return has_consumer as False, so that it would create a new consumer.
    monkeypatch.setattr('auth_api.services.api_gateway.ApiGateway._consumer_exists', lambda *args, **kwargs: None)

    def get_pay_account_mock(org, user):
        return {
            'paymentMethod': 'PAD'
        }

    monkeypatch.setattr('auth_api.services.api_gateway.ApiGateway._get_pay_account', get_pay_account_mock)
    monkeypatch.setattr('auth_api.services.api_gateway.ApiGateway._create_sandbox_pay_account',
                        lambda *args, **kwargs: None)

    rv = client.post(f'/api/v1/orgs/{org_id}/api-keys', headers=headers, content_type='application/json',
                     data=json.dumps({
                         'environment': 'sandbox',
                         'keyName': 'TEST'
                     }))
    assert rv.json['consumer']['consumerKey']

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get(f'/api/v1/orgs/{org_id}', headers=headers, content_type='application/json')
    assert rv.json.get('hasApiAccess')


@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
def test_list_api_keys(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that api keys can be listed."""
    # First create an account
    user_header = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
    client.post('/api/v1/users', headers=user_header, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1), headers=user_header,
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

    rv = client.get(f'/api/v1/orgs/{org_id}/api-keys', headers=user_header, content_type='application/json')
    assert rv.json['consumer']['consumerKey']


@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
def test_revoke_api_key(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that api keys can be revoked."""
    # First create an account
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
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
    key = rv.json['consumer']['consumerKey'][0]['apiKey']

    rv = client.delete(f'/api/v1/orgs/{org_id}/api-keys/{key}', headers=headers, content_type='application/json')
    assert rv.status_code == 200

    # Revoke an invalid key
    rv = client.delete(f'/api/v1/orgs/{org_id}/api-keys/{key}-INVALID', headers=user_headers,
                       content_type='application/json')
    assert rv.status_code == 404

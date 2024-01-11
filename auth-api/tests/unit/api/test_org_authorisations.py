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

"""Tests to verify the orgs API end-point.

Test-Suite to ensure that the /orgs/authorisations endpoint is working as expected.
"""

import json
import mock

from auth_api import status as http_status
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo, TestOrgProductsInfo
from tests.utilities.factory_utils import factory_auth_header
from tests.conftest import mock_token


@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
def test_add_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    orgs = json.loads(rv.data)
    id = orgs.get('id')
    rv = client.get(f'/api/v1/orgs/{id}/authorizations',
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    org_authorisations = json.loads(rv.data)
    assert org_authorisations.get('orgMembership') == 'ADMIN'
    assert org_authorisations.get('roles')

    # NR should have all access since its internal
    headers.update({'Product-Code': 'NRO'})
    rv = client.get(f'/api/v1/orgs/{id}/authorizations',
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    org_authorisations_by_nro = json.loads(rv.data)
    assert org_authorisations_by_nro.get('orgMembership') == 'ADMIN', 'NR should get admin access'
    assert org_authorisations_by_nro.get('roles')

    # vital stats shouldn't get any access since its partner
    headers.update({'Product-Code': 'VS'})
    rv = client.get(f'/api/v1/orgs/{id}/authorizations',
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    org_authorisations_by_vs = json.loads(rv.data)
    assert len(org_authorisations_by_vs.get('roles')) == 0


@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
def test_ppr_auth(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that accounts get PPR authorization."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    # Create a basic account
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    orgs = json.loads(rv.data)
    id = orgs.get('id')

    # Try to add PPR as a product which doesn't add product as account is BASIC.
    client.post(f'/api/v1/orgs/{id}/products',
                data=json.dumps(TestOrgProductsInfo.org_products1),
                headers=headers, content_type='application/json')
    # Check PPR access and assert no roles are returned.
    rv = client.get(f'/api/v1/accounts/{id}/products/PPR/authorizations',
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK

    org_authorisations = json.loads(rv.data)
    assert len(org_authorisations.get('roles')) == 0

    # Create a PREMIUM account
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.bcol_linked()),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    orgs = json.loads(rv.data)
    id = orgs.get('id')
    # Try to add PPR as a product which adds product as account is PREMIUM.
    client.post(f'/api/v1/orgs/{id}/products',
                data=json.dumps(TestOrgProductsInfo.org_products1),
                headers=headers, content_type='application/json')
    # Check PPR access and assert no roles are returned.
    rv = client.get(f'/api/v1/accounts/{id}/products/PPR/authorizations', headers=headers,
                    content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    org_authorisations = json.loads(rv.data)
    assert len(org_authorisations.get('roles')) > 0

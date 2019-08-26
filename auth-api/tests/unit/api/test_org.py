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

Test-Suite to ensure that the /orgs endpoint is working as expected.
"""

import json
import os

from auth_api import status as http_status


TEST_ORG_INFO = {
    'name': 'My Test Org'
}

TEST_INVALID_ORG_INFO = {
    'foo': 'bar'
}

TEST_CONTACT_INFO = {
    'email': 'foo@bar.com',
    'phone': '(555) 555-5555',
    'phoneExtension': '123'
}

TEST_UPDATED_CONTACT_INFO = {
    'email': 'bar@foo.com',
    'phone': '(555) 555-5555',
    'phoneExtension': '123'
}

TEST_INVALID_CONTACT_INFO = {
    'email': 'bar'
}

TEST_JWT_CLAIMS = {
    'iss': os.getenv('JWT_OIDC_ISSUER'),
    'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
    'firstname': 'Test',
    'lastname': 'User',
    'preferred_username': 'testuser',
    'realm_access': {
        'roles': [
            'basic'
        ]
    }
}

TEST_JWT_HEADER = {
    'alg': os.getenv('JWT_OIDC_ALGORITHMS'),
    'typ': 'JWT',
    'kid': os.getenv('JWT_OIDC_AUDIENCE')
}


def factory_auth_header(jwt, claims):
    """Produce JWT tokens for use in tests."""
    return {'Authorization': 'Bearer ' + jwt.create_jwt(claims=claims, header=TEST_JWT_HEADER)}


def test_add_org(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_add_org_invalid_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 400."""
    headers = factory_auth_header(jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_INVALID_ORG_INFO),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_get_org(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an org can be retrieved via GET."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.get('/api/v1/orgs/{}'.format(org_id),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['id'] == org_id


def test_get_org_no_auth_returns_401(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an org cannot be retrieved without an authorization header."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.get('/api/v1/orgs/{}'.format(org_id),
                    headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_get_org_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that attempting to retrieve a non-existent org returns a 404."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.get('/api/v1/orgs/{}'.format(999),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_add_contact(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an org."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                     headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TEST_CONTACT_INFO['email']


def test_add_contact_invalid_format_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding an invalidly formatted contact returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                     headers=headers, data=json.dumps(TEST_INVALID_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_contact_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact to a non-existant org returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/orgs/{}/contacts'.format(99),
                     headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_add_contact_duplicate_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a duplicate contact to an org returns 400."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    rv = client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                     headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a contact can be updated on an org."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                     headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    rv = client.put('/api/v1/orgs/{}/contacts'.format(org_id),
                    headers=headers, data=json.dumps(TEST_UPDATED_CONTACT_INFO), content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TEST_UPDATED_CONTACT_INFO['email']


def test_update_contact_invalid_format_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating with an invalidly formatted contact returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    rv = client.put('/api/v1/orgs/{}/contacts'.format(org_id),
                    headers=headers, data=json.dumps(TEST_INVALID_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating a contact on a non-existant entity returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.put('/api/v1/orgs/{}/contacts'.format(99),
                    headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_update_contact_missing_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating a non-existant contact returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.put('/api/v1/orgs/{}/contacts'.format(org_id),
                    headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND

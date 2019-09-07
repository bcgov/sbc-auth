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

"""Tests to verify the entities API end-point.

Test-Suite to ensure that the /entities endpoint is working as expected.
"""

import copy
import json
import os

from tests.utilities.factory_utils import *

from auth_api import status as http_status


TEST_ENTITY_INFO = {
    'businessIdentifier': 'CP1234567',
    'businessNumber': '791861073BC0001',
    'name': 'Foobar, Inc.'
}

TEST_INVALID_ENTITY_INFO = {
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


def test_add_entity(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an entity can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_add_entity_invalid_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid entity returns a 400."""
    headers = factory_auth_header(jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/entities', data=json.dumps(TEST_INVALID_ENTITY_INFO),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_entity_no_auth_returns_401(client, session):  # pylint:disable=unused-argument
    """Assert that POSTing an entity without an auth header returns a 401."""
    rv = client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                     headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_add_entity_duplicate_returns_409(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an entity that already exists returns a 409."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                     headers=headers, content_type='application/json')
    rv = client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_409_CONFLICT


def test_get_entity(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an entity can be retrieved via GET."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                headers=headers, content_type='application/json')
    rv = client.get('/api/v1/entities/{}'.format(TEST_ENTITY_INFO['businessIdentifier']),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['businessIdentifier'] == TEST_ENTITY_INFO['businessIdentifier']


def test_get_entity_no_auth_returns_401(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an entity cannot be retrieved without an authorization header."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                headers=headers, content_type='application/json')
    rv = client.get('/api/v1/entities/{}'.format(TEST_ENTITY_INFO['businessIdentifier']),
                    headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_get_entity_no_entity_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that attempting to retrieve a non-existent entity returns a 404."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.get('/api/v1/entities/{}'.format(TEST_ENTITY_INFO['businessIdentifier']),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_add_contact(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an entity."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                headers=headers, content_type='application/json')
    rv = client.post('/api/v1/entities/{}/contacts'.format(TEST_ENTITY_INFO['businessIdentifier']),
                     headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TEST_CONTACT_INFO['email']


def test_add_contact_invalid_format_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding an invalidly formatted contact returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                headers=headers, content_type='application/json')
    rv = client.post('/api/v1/entities/{}/contacts'.format(TEST_ENTITY_INFO['businessIdentifier']),
                     headers=headers, data=json.dumps(TEST_INVALID_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_contact_no_entity_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact to a non-existant Entity returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/entities/{}/contacts'.format(TEST_ENTITY_INFO['businessIdentifier']),
                     headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_add_contact_duplicate_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a duplicate contact to an Entity returns 400."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                headers=headers, content_type='application/json')
    client.post('/api/v1/entities/{}/contacts'.format(TEST_ENTITY_INFO['businessIdentifier']),
                headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    rv = client.post('/api/v1/entities/{}/contacts'.format(TEST_ENTITY_INFO['businessIdentifier']),
                     headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a contact can be updated on an entity."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                headers=headers, content_type='application/json')
    rv = client.post('/api/v1/entities/{}/contacts'.format(TEST_ENTITY_INFO['businessIdentifier']),
                     headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    rv = client.put('/api/v1/entities/{}/contacts'.format(TEST_ENTITY_INFO['businessIdentifier']),
                    headers=headers, data=json.dumps(TEST_UPDATED_CONTACT_INFO), content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TEST_UPDATED_CONTACT_INFO['email']


def test_update_contact_invalid_format_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating with an invalidly formatted contact returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                headers=headers, content_type='application/json')
    client.post('/api/v1/entities/{}/contacts'.format(TEST_ENTITY_INFO['businessIdentifier']),
                headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    rv = client.put('/api/v1/entities/{}/contacts'.format(TEST_ENTITY_INFO['businessIdentifier']),
                    headers=headers, data=json.dumps(TEST_INVALID_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact_no_entity_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating a contact on a non-existant entity returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.put('/api/v1/entities/{}/contacts'.format(TEST_ENTITY_INFO['businessIdentifier']),
                    headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_update_contact_missing_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating a non-existant contact returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    client.post('/api/v1/entities', data=json.dumps(TEST_ENTITY_INFO),
                headers=headers, content_type='application/json')
    rv = client.put('/api/v1/entities/{}/contacts'.format(TEST_ENTITY_INFO['businessIdentifier']),
                    headers=headers, data=json.dumps(TEST_CONTACT_INFO), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_authorizations_passcode_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for passcode user returns 200."""
    claims = copy.deepcopy(TEST_JWT_CLAIMS)
    claims['username'] = inc_number = 'CP123456789'
    claims['loginSource'] = 'PASSCODE'

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f'/api/v1/entities/{inc_number}/authorizations',
                headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('role') == 'OWNER'

    # Test with invalid number
    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get('/api/v1/entities/INVALID/authorizations',
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('role', None) is None


def test_authorizations_for_staff_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for staff user returns 200."""
    claims = copy.deepcopy(TEST_JWT_CLAIMS)
    claims['username'] = inc_number = 'tester'
    claims['loginSource'] = ''
    claims['realm_access']['roles'].append('staff')

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f'/api/v1/entities/{inc_number}/authorizations',
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('role') == 'STAFF'


def test_authorizations_for_affiliated_users_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for affiliated users returns 200."""
    user = factory_user_model()
    org = factory_org_model('TEST')
    factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    claims = copy.deepcopy(TEST_JWT_CLAIMS)
    claims['sub'] = str(user.keycloak_guid)

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f'/api/v1/entities/{entity.business_identifier}/authorizations',
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('role') == 'OWNER'

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
import json
import os

from tests.utilities.factory_utils import *

from auth_api import status as http_status
from auth_api.exceptions.errors import Error


TEST_JWT_CLAIMS = {
    'iss': os.getenv('JWT_OIDC_ISSUER'),
    'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
    'firstname': 'Test',
    'lastname': 'User',
    'preferred_username': 'testuser'
}

TEST_JWT_CLAIMS_2 = {
    'iss': os.getenv('JWT_OIDC_ISSUER'),
    'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302065',
    'firstname': 'Test',
    'lastname': 'User 2',
    'preferred_username': 'testuser2'
}

TEST_JWT_INVALID_CLAIMS = {
    'iss': 'foobar',
    'sub': 'barfoo',
    'firstname': 'Trouble',
    'lastname': 'Maker',
    'preferred_username': 'troublemaker'
}

TEST_STAFF_JWT_CLAIMS = {
    'iss': os.getenv('JWT_OIDC_ISSUER'),
    'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302066',
    'firstname': 'Test_Staff',
    'lastname': 'User',
    'preferred_username': 'testuser',
    'realm_access': {
        'roles': [
            'staff'
        ]
    }
}

UPDATED_TEST_JWT_CLAIMS = {
    'iss': os.getenv('JWT_OIDC_ISSUER'),
    'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
    'firstname': 'Updated_Test',
    'lastname': 'User',
    'username': 'testuser'
}

TEST_JWT_HEADER = {
    'alg': os.getenv('JWT_OIDC_ALGORITHMS'),
    'typ': 'JWT',
    'kid': os.getenv('JWT_OIDC_AUDIENCE')
}

TEST_CONTACT = {
    'email': 'foo@bar.com',
    'phone': '(555) 555-5555',
    'phoneExtension': '123'
}

UPDATED_TEST_CONTACT = {
    'email': 'bar@foo.com',
    'phone': '(555) 555-5555',
    'phoneExtension': '123'
}

INVALID_TEST_CONTACT = {
    'email': 'bar'
}

TEST_ORG_INFO = {
    'name': 'My Test Org'
}


def test_add_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user can be POSTed."""
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_add_user_no_token_returns_401(client, session):  # pylint:disable=unused-argument
    """Assert that POSTing a user with no token returns a 401."""
    rv = client.post('/api/v1/users', headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_add_user_invalid_token_returns_401(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing a user with an invalid token returns a 401."""
    token = jwt.create_jwt(claims=TEST_JWT_INVALID_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_update_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a POST to an existing user updates that user."""
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    user = json.loads(rv.data)
    assert user['firstname'] == 'Test'

    # post token with updated claims
    token = jwt.create_jwt(claims=UPDATED_TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    user = json.loads(rv.data)
    assert user['firstname'] == 'Updated_Test'


def test_staff_get_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a staff user can GET a user by id."""
    # POST a test user
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # GET the test user as a staff user
    token = jwt.create_jwt(claims=TEST_STAFF_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.get('/api/v1/users/{}'.format(TEST_JWT_CLAIMS['preferred_username']),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    user = json.loads(rv.data)
    assert user['firstname'] == 'Test'


def test_staff_get_user_invalid_id_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a staff user can GET a user by id."""
    token = jwt.create_jwt(claims=TEST_STAFF_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.get('/api/v1/users/{}'.format('SOME_USER'), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_staff_search_users(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a staff user can GET a list of users with search parameters."""
    # POST a test user
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # POST a second test user
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS_2, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # Search on all users as a staff user
    token = jwt.create_jwt(claims=TEST_STAFF_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.get('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    users = json.loads(rv.data)
    assert len(users) == 2

    # Search on users with a search parameter
    rv = client.get('/api/v1/users?lastname={}'.format(TEST_JWT_CLAIMS_2['lastname']),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    users = json.loads(rv.data)
    assert len(users) == 1


def test_get_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user can retrieve their own profile."""
    # POST a test user
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    rv = client.get('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    user = json.loads(rv.data)
    assert user['firstname'] == 'Test'


def test_get_user_returns_401(client, session):  # pylint:disable=unused-argument
    """Assert that unauthorized access to a user profile returns a 401 error."""
    rv = client.get('/api/v1/users/@me', headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_get_user_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the endpoint returns 404 when user is not found."""
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.get('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == Error.DATA_NOT_FOUND.status_code


def test_add_contact(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a contact can be added (POST) to an existing user."""
    # POST a test user
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # POST a contact to test user
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TEST_CONTACT),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    user = json.loads(rv.data)
    assert len(user['contacts']) == 1
    assert user['contacts'][0]['email'] == 'foo@bar.com'


def test_add_contact_no_token_returns_401(client, session):  # pylint:disable=unused-argument
    """Assert that adding a contact without providing a token returns a 401."""
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TEST_CONTACT),
                     headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_add_contact_invalid_format_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact in an invalid format returns a 400."""
    # POST a test user
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.post('/api/v1/users/contacts', data=json.dumps(INVALID_TEST_CONTACT),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_contact_duplicate_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact for a user who already has a contact returns a 400."""
    # POST a test user
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # POST a contact to test user
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TEST_CONTACT),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    rv = client.post('/api/v1/users/contacts', data=json.dumps(UPDATED_TEST_CONTACT),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact(client, jwt, session):  # pylint:disable=unused-argument, invalid-name
    """Assert that a contact can be updated (PUT) on an existing user."""
    # POST a test user
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # POST a contact to test user
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TEST_CONTACT),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # PUT a contact on the same user
    rv = client.put('/api/v1/users/contacts', data=json.dumps(UPDATED_TEST_CONTACT),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    user = json.loads(rv.data)
    assert len(user['contacts']) == 1
    assert user['contacts'][0]['email'] == 'bar@foo.com'


def test_update_contact_no_token_returns_401(client, session):  # pylint:disable=unused-argument
    """Assert that updating a contact without providing a token returns a 401."""
    rv = client.put('/api/v1/users/contacts', data=json.dumps(UPDATED_TEST_CONTACT),
                    headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_update_contact_invalid_format_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact in an invalid format returns a 400."""
    # POST a test user
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.put('/api/v1/users/contacts', data=json.dumps(INVALID_TEST_CONTACT),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact_missing_contact_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating a contact for a non-existent user returns a 404."""
    # POST a test user
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # PUT a contact to test user
    rv = client.put('/api/v1/users/contacts', data=json.dumps(TEST_CONTACT),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_delete_contact(client, jwt, session):  # pylint:disable=unused-argument, invalid-name
    """Assert that a contact can be deleted on an existing user."""
    # POST a test user
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # POST a contact to test user
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TEST_CONTACT),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # PUT a contact on the same user
    rv = client.delete('/api/v1/users/contacts', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    user = json.loads(rv.data)
    assert user.get('contacts') == []


def test_delete_contact_no_token_returns_401(client, session):  # pylint:disable=unused-argument, invalid-name
    """Assert that deleting a contact without a token returns a 401."""
    rv = client.delete('/api/v1/users/contacts', headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_delete_contact_no_contact_returns_404(client, jwt, session):  # pylint:disable=unused-argument, invalid-name
    """Assert that deleting a contact that doesn't exist returns a 404."""
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.delete('/api/v1/users/contacts', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_get_orgs_for_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that retrieving a list of orgs for a user functions."""
    token = jwt.create_jwt(claims=TEST_JWT_CLAIMS, header=TEST_JWT_HEADER)
    headers = {'Authorization': 'Bearer ' + token}
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # Add an org - the current user should be auto-added as an OWNER
    rv = client.post('/api/v1/orgs', headers=headers, data=json.dumps(TEST_ORG_INFO), content_type='application/json')

    rv = client.get('/api/v1/users/orgs', headers=headers)

    assert rv.status_code == http_status.HTTP_200_OK

    response = json.loads(rv.data)
    assert response['orgs']
    assert len(response['orgs']) == 1
    assert response['orgs'][0]['name'] == TEST_ORG_INFO['name']


def test_user_authorizations_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for users returns 200."""

    user = factory_user_model()
    org = factory_org_model('TEST')
    factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    claims = copy.deepcopy(TEST_JWT_CLAIMS)
    claims['sub'] = str(user.keycloak_guid)

    token = jwt.create_jwt(header=TEST_JWT_HEADER, claims=claims)
    headers = {'Authorization': f'Bearer {token}'}
    rv = client.get('/api/v1/users/authorizations', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('authorizations')[0].get('role') == 'OWNER'

    # Test with invalid user
    claims['sub'] = str(uuid.uuid4())
    token = jwt.create_jwt(header=TEST_JWT_HEADER, claims=claims)
    headers = {'Authorization': f'Bearer {token}'}

    rv = client.get('/api/v1/users/authorizations', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert len(rv.json.get('authorizations')) == 0

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

"""Tests to verify the invitations API end-point.

Test-Suite to ensure that the /invitations endpoint is working as expected.
"""

import json
import os

from auth_api import status as http_status


TEST_ORG_INFO = {
    'name': 'My Test Org'
}

TEST_JWT_CLAIMS = {
    'iss': os.getenv('JWT_OIDC_ISSUER'),
    'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
    'firstname': 'Test',
    'lastname': 'User',
    'preferred_username': 'testuser',
    'realm_access': {
        'roles': [
            'edit'
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


def test_add_invitation(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an invitation can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    new_invitation = {
        'recipientEmail': 'test@abc.com',
        'sentDate': '2019-09-09',
        'membership': [
            {
                'membershipType': 'MEMBER',
                'orgId': str(org_id)
            }
        ]
    }
    rv = client.post('/api/v1/invitations', data=json.dumps(new_invitation),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_add_invitation_invalid(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid invitation returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')

    new_invitation = {
        'recipientEmail': 'test@abc.com'
    }
    rv = client.post('/api/v1/invitations', data=json.dumps(new_invitation),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_get_invitations_by_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an invitation by a user can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    new_invitation = {
        'recipientEmail': 'test@abc.com',
        'sentDate': '2019-09-09',
        'membership': [
            {
                'membershipType': 'MEMBER',
                'orgId': str(org_id)
            }
        ]
    }
    rv = client.post('/api/v1/invitations', data=json.dumps(new_invitation),
                     headers=headers, content_type='application/json')
    rv = client.get('/api/v1/invitations', headers=headers, content_type='application/json')
    invitation_dict = json.loads(rv.data)
    assert rv.status_code == http_status.HTTP_200_OK
    assert invitation_dict['invitations']
    assert len(invitation_dict['invitations']) == 1


def test_get_invitations_by_id(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an invitation can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    new_invitation = {
        'recipientEmail': 'test@abc.com',
        'sentDate': '2019-09-09',
        'membership': [
            {
                'membershipType': 'MEMBER',
                'orgId': str(org_id)
            }
        ]
    }
    rv = client.post('/api/v1/invitations', data=json.dumps(new_invitation),
                     headers=headers, content_type='application/json')
    invitation_dictionary = json.loads(rv.data)
    invitation_id = invitation_dictionary['id']
    rv = client.get('/api/v1/invitations/{}'.format(invitation_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK


def test_delete_invitation(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an invitation can be deleted."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    new_invitation = {
        'recipientEmail': 'test@abc.com',
        'sentDate': '2019-09-09',
        'membership': [
            {
                'membershipType': 'MEMBER',
                'orgId': str(org_id)
            }
        ]
    }
    rv = client.post('/api/v1/invitations', data=json.dumps(new_invitation),
                     headers=headers, content_type='application/json')
    invitation_dictionary = json.loads(rv.data)
    invitation_id = invitation_dictionary['id']
    rv = client.delete('/api/v1/invitations/{}'.format(invitation_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    rv = client.get('/api/v1/invitations/{}'.format(invitation_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND
    dictionary = json.loads(rv.data)
    assert dictionary['message'] == 'The requested invitation could not be found.'


def test_update_invitation(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an invitation can be updated."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TEST_ORG_INFO),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    new_invitation = {
        'recipientEmail': 'test@abc.com',
        'sentDate': '2019-09-09',
        'membership': [
            {
                'membershipType': 'MEMBER',
                'orgId': str(org_id)
            }
        ]
    }
    rv = client.post('/api/v1/invitations', data=json.dumps(new_invitation),
                     headers=headers, content_type='application/json')
    invitation_dictionary = json.loads(rv.data)
    invitation_id = invitation_dictionary['id']
    updated_invitation = {
        'status': 'ACCEPTED',
        'acceptedDate': '2019-09-11T00:00:00+00:00'
    }
    rv = client.put('/api/v1/invitations/{}'.format(invitation_id),
                    data=json.dumps(updated_invitation), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['status'] == updated_invitation['status']

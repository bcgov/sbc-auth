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

import pytest

from auth_api import status as http_status
from auth_api.schemas import utils as schema_utils
from auth_api.services import Invitation as InvitationService
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.constants import GROUP_GOV_ACCOUNT_USERS, GROUP_PUBLIC_USERS
from tests.utilities.factory_scenarios import KeycloakScenario, TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_auth_header, factory_invitation


KEYCLOAK_SERVICE = KeycloakService()


@pytest.mark.parametrize('org_info, role, claims', [
    (TestOrgInfo.org_regular, 'ADMIN', TestJwtClaims.public_user_role),
    (TestOrgInfo.org_regular, 'USER', TestJwtClaims.public_user_role),
    (TestOrgInfo.org_regular, 'COORDINATOR', TestJwtClaims.public_user_role),
    (TestOrgInfo.org_regular_bceid, 'ADMIN', TestJwtClaims.public_bceid_user),
    (TestOrgInfo.org_regular_bceid, 'USER', TestJwtClaims.public_bceid_user),
    (TestOrgInfo.org_regular_bceid, 'COORDINATOR', TestJwtClaims.public_bceid_user)
])
def test_add_invitation(client, jwt, session, keycloak_mock, org_info, role, claims):  # pylint:disable=unused-argument
    """Assert that an invitation can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(org_info), headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id=org_id, membership_type=role)),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    assert dictionary.get('token') is not None
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv.json, 'invitation_response')[0]


def test_add_invitation_invalid(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid invitation returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id=None)),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_get_invitations_by_id(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an invitation can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id=org_id)),
                     headers=headers, content_type='application/json')
    invitation_dictionary = json.loads(rv.data)
    invitation_id = invitation_dictionary['id']
    rv = client.get('/api/v1/invitations/{}'.format(invitation_id), headers=headers, content_type='application/json')
    assert schema_utils.validate(rv.json, 'invitation_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK


def test_delete_invitation(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an invitation can be deleted."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id=org_id)),
                     headers=headers, content_type='application/json')
    invitation_dictionary = json.loads(rv.data)
    invitation_id = invitation_dictionary['id']
    rv = client.delete('/api/v1/invitations/{}'.format(invitation_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK

    rv = client.get('/api/v1/invitations/{}'.format(invitation_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND
    dictionary = json.loads(rv.data)
    assert dictionary['message'] == 'The requested invitation could not be found.'


def test_update_invitation(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an invitation can be updated."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id=org_id)),
                     headers=headers, content_type='application/json')
    invitation_dictionary = json.loads(rv.data)
    invitation_id = invitation_dictionary['id']
    updated_invitation = {}
    rv = client.patch('/api/v1/invitations/{}'.format(invitation_id), data=json.dumps(updated_invitation),
                      headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'invitation_response')[0]
    dictionary = json.loads(rv.data)
    assert dictionary['status'] == 'PENDING'


def test_validate_token(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a token is valid."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id=org_id)),
                     headers=headers, content_type='application/json')
    invitation_dictionary = json.loads(rv.data)
    invitation_id = invitation_dictionary['id']
    invitation_id_token = InvitationService.generate_confirmation_token(invitation_id)
    rv = client.get('/api/v1/invitations/tokens/{}'.format(invitation_id_token), headers=headers,
                    content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK


def test_accept_public_users_invitation(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an invitation can be accepted."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id=org_id)),
                     headers=headers, content_type='application/json')
    invitation_dictionary = json.loads(rv.data)
    invitation_id = invitation_dictionary['id']
    invitation_id_token = InvitationService.generate_confirmation_token(invitation_id)

    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id
    headers_invitee = factory_auth_header(jwt=jwt, claims=TestJwtClaims.get_test_user(user_id, source='BCSC'))
    client.post('/api/v1/users', headers=headers_invitee, content_type='application/json')
    rv = client.put('/api/v1/invitations/tokens/{}'.format(invitation_id_token), headers=headers_invitee,
                    content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK

    rv = client.get('/api/v1/orgs/{}/members?status=PENDING_APPROVAL'.format(org_id),
                    headers=headers,
                    content_type='application/json')
    dictionary = json.loads(rv.data)
    assert len(dictionary['members']) == 1
    # Assert that the user got added to the keycloak groups
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_PUBLIC_USERS in groups


@pytest.mark.skip(reason='This is wrong test case')
def test_accept_gov_account_invitation(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an invitation can be accepted."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.gov_account_holder_user)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id=org_id)),
                     headers=headers, content_type='application/json')
    invitation_dictionary = json.loads(rv.data)
    invitation_id = invitation_dictionary['id']
    invitation_id_token = InvitationService.generate_confirmation_token(invitation_id)

    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id
    headers_invitee = factory_auth_header(jwt=jwt, claims=TestJwtClaims.get_test_user(user_id, source='IDIR', roles=[]))
    client.post('/api/v1/users', headers=headers_invitee, content_type='application/json')
    rv = client.put('/api/v1/invitations/tokens/{}'.format(invitation_id_token), headers=headers_invitee,
                    content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK

    rv = client.get('/api/v1/orgs/{}/members?status=PENDING_APPROVAL'.format(org_id),
                    headers=headers,
                    content_type='application/json')
    dictionary = json.loads(rv.data)
    assert len(dictionary['members']) == 1
    # Assert that the user got added to the keycloak groups
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_GOV_ACCOUNT_USERS in groups

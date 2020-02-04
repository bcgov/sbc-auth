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
import uuid

from auth_api import status as http_status
from auth_api.exceptions.errors import Error
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.services import Org as OrgService
from auth_api.utils.roles import Status
from tests import skip_in_pod
from tests.utilities.factory_scenarios import TestContactInfo, TestEntityInfo, TestJwtClaims, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import (
    factory_affiliation_model, factory_auth_header, factory_contact_model, factory_entity_model,
    factory_membership_model, factory_org_model, factory_user_model)


def test_add_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_add_user_no_token_returns_401(client, session):  # pylint:disable=unused-argument
    """Assert that POSTing a user with no token returns a 401."""
    rv = client.post('/api/v1/users', headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


@skip_in_pod
def test_add_user_invalid_token_returns_401(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing a user with an invalid token returns a 401."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.invalid)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_update_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a POST to an existing user updates that user."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    user = json.loads(rv.data)
    assert user['firstname'] == 'Test'

    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.updated_test)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    user = json.loads(rv.data)
    assert user['firstname'] == 'Updated_Test'


def test_update_user_terms_of_use(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a PATCH to an existing user updates that user."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    user = json.loads(rv.data)
    assert user['firstname'] == 'Test'

    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.updated_test)
    input_data = json.dumps({'termsversion': 1, 'istermsaccepted': True})
    rv = client.patch('/api/v1/users/@me', headers=headers,
                      data=input_data, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    user = json.loads(rv.data)
    assert user['userTerms']['termsOfUseAcceptedVersion'] == 1


def test_update_user_terms_of_use_invalid_input(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a PATCH to an existing user updates that user."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    user = json.loads(rv.data)
    assert user['firstname'] == 'Test'

    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.updated_test)
    input_data = json.dumps({'invalid': True})
    rv = client.patch('/api/v1/users/@me', headers=headers,
                      data=input_data, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_user_terms_of_use_no_jwt(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a PATCH to an existing user updates that user."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    user = json.loads(rv.data)
    assert user['firstname'] == 'Test'

    # post token with updated claims
    input_data = json.dumps({'invalid': True})
    rv = client.patch('/api/v1/users/@me',
                      data=input_data, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_staff_get_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a staff user can GET a user by id."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # GET the test user as a staff user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/users/{}'.format(TestJwtClaims.edit_role['preferred_username']),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    user = json.loads(rv.data)
    assert user['firstname'] == 'Test'


def test_staff_get_user_invalid_id_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a staff user can GET a user by id."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/users/{}'.format('SOME_USER'), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_staff_search_users(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a staff user can GET a list of users with search parameters."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # POST a second test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.no_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # Search on all users as a staff user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    users = json.loads(rv.data)
    assert len(users) == 2

    # Search on users with a search parameter
    rv = client.get('/api/v1/users?lastname={}'.format(TestJwtClaims.no_role['lastname']),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    users = json.loads(rv.data)
    assert len(users) == 1


def test_get_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user can retrieve their own profile."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
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
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.get('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == Error.DATA_NOT_FOUND.status_code


def test_add_contact(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a contact can be added (POST) to an existing user."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # POST a contact to test user
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    contact = json.loads(rv.data)
    assert contact['email'] == 'foo@bar.com'


def test_add_contact_valid_email_with_special_characters(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a contact can be added (POST) to an existing user."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # POST a contact to test user
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.email_valid),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    contact = json.loads(rv.data)
    assert contact['email'] == TestContactInfo.email_valid['email']


def test_add_contact_no_token_returns_401(client, session):  # pylint:disable=unused-argument
    """Assert that adding a contact without providing a token returns a 401."""
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact1),
                     headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_add_contact_invalid_format_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact in an invalid format returns a 400."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.invalid),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_contact_duplicate_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact for a user who already has a contact returns a 400."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # POST a contact to test user
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    rv = client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact2),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact(client, jwt, session):  # pylint:disable=unused-argument, invalid-name
    """Assert that a contact can be updated (PUT) on an existing user."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # POST a contact to test user
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # PUT a contact on the same user
    rv = client.put('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact2),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    contact = json.loads(rv.data)
    assert contact['email'] == 'bar@foo.com'


def test_update_contact_no_token_returns_401(client, session):  # pylint:disable=unused-argument
    """Assert that updating a contact without providing a token returns a 401."""
    rv = client.put('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact2),
                    headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_update_contact_invalid_format_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact in an invalid format returns a 400."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.put('/api/v1/users/contacts', data=json.dumps(TestContactInfo.invalid),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact_missing_contact_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating a contact for a non-existent user returns a 404."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # PUT a contact to test user
    rv = client.put('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact1),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_delete_contact(client, jwt, session):  # pylint:disable=unused-argument, invalid-name
    """Assert that a contact can be deleted on an existing user."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # POST a contact to test user
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # PUT a contact on the same user
    rv = client.delete('/api/v1/users/contacts', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK

    rv = client.get('/api/v1/users/contacts', headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    contacts = dictionary.get('contacts')
    assert len(contacts) == 0


def test_delete_contact_no_token_returns_401(client, session):  # pylint:disable=unused-argument, invalid-name
    """Assert that deleting a contact without a token returns a 401."""
    rv = client.delete('/api/v1/users/contacts', headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_delete_contact_no_contact_returns_404(client, jwt, session):  # pylint:disable=unused-argument, invalid-name
    """Assert that deleting a contact that doesn't exist returns a 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.delete('/api/v1/users/contacts', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_get_orgs_for_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that retrieving a list of orgs for a user functions."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # Add an org - the current user should be auto-added as an OWNER
    rv = client.post('/api/v1/orgs', headers=headers, data=json.dumps(TestOrgInfo.org1),
                     content_type='application/json')

    rv = client.get('/api/v1/users/orgs', headers=headers)

    assert rv.status_code == http_status.HTTP_200_OK

    response = json.loads(rv.data)
    assert response['orgs']
    assert len(response['orgs']) == 1
    assert response['orgs'][0]['name'] == TestOrgInfo.org1['name']


def test_user_authorizations_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for users returns 200."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    claims = copy.deepcopy(TestJwtClaims.edit_role.value)
    claims['sub'] = str(user.keycloak_guid)

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get('/api/v1/users/authorizations', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('authorizations')[0].get('orgMembership') == 'OWNER'

    # Test with invalid user
    claims['sub'] = str(uuid.uuid4())
    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get('/api/v1/users/authorizations', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert len(rv.json.get('authorizations')) == 0


def test_delete_user_with_no_orgs_returns_204(client, jwt, session):  # pylint:disable=unused-argument
    """Test if the user doesn't have any teams/orgs assert status is 204."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.updated_test)

    rv = client.delete('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT


def test_delete_inactive_user_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Test if the user doesn't have any teams/orgs assert status is 204."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.updated_test)

    rv = client.delete('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT

    rv = client.delete('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_delete_unknown_user_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Test if the user doesn't have any teams/orgs assert status is 204."""
    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.updated_test)

    rv = client.delete('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_delete_user_as_only_admin_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Test if the user is the only owner of a team assert status is 400."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.commit()

    org = OrgService.create_org(TestOrgInfo.org1, user_id=user_model.id)
    org_dictionary = org.as_dict()
    org_id = org_dictionary['id']

    entity = factory_entity_model(entity_info=TestEntityInfo.entity_lear_mock)

    affiliation = AffiliationModel(org_id=org_id, entity_id=entity.id)
    affiliation.save()

    claims = copy.deepcopy(TestJwtClaims.edit_role.value)
    claims['sub'] = str(user_model.keycloak_guid)

    headers = factory_auth_header(jwt=jwt, claims=claims)

    rv = client.delete('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_delete_user_is_member_returns_204(client, jwt, session):  # pylint:disable=unused-argument
    """Test if the user is the member of a team assert status is 204."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.commit()

    org = OrgService.create_org(TestOrgInfo.org1, user_id=user_model.id)
    org_dictionary = org.as_dict()
    org_id = org_dictionary['id']

    entity = factory_entity_model(entity_info=TestEntityInfo.entity_lear_mock)
    affiliation = AffiliationModel(org_id=org_id, entity_id=entity.id)
    affiliation.save()

    user_model2 = factory_user_model(user_info=TestUserInfo.user2)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model2
    contact_link.commit()

    membership = MembershipModel(org_id=org_id, user_id=user_model2.id, membership_type_code='MEMBER',
                                 membership_type_status=Status.ACTIVE.value)
    membership.save()

    claims = copy.deepcopy(TestJwtClaims.edit_role.value)
    claims['sub'] = str(user_model2.keycloak_guid)

    headers = factory_auth_header(jwt=jwt, claims=claims)

    rv = client.delete('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT


def test_delete_user_with_tester_role(client, jwt, session):  # pylint:disable=unused-argument
    """Test delete the user by tester role assert status is 204."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.tester_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.tester_role)

    rv = client.delete('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT

    rv = client.get('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND

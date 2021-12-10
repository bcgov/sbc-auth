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
import time
import uuid

from auth_api import status as http_status
from auth_api.exceptions.errors import Error
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.schemas import utils as schema_utils
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.enums import AccessType, IdpHint, ProductCode, Status, UserStatus
from auth_api.utils.roles import ADMIN, COORDINATOR, USER, Role
from tests import skip_in_pod
from tests.utilities.factory_scenarios import (
    KeycloakScenario, TestAffidavit, TestAnonymousMembership, TestContactInfo, TestEntityInfo, TestJwtClaims,
    TestOrgInfo, TestOrgTypeInfo, TestUserInfo)
from tests.utilities.factory_utils import (
    factory_affiliation_model, factory_auth_header, factory_contact_model, factory_entity_model,
    factory_invitation_anonymous, factory_membership_model, factory_org_model, factory_product_model,
    factory_user_model, patch_token_info)


KEYCLOAK_SERVICE = KeycloakService()


def test_add_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv.json, 'user_response')[0]


def test_delete_bcros_valdiations(client, jwt, session, keycloak_mock, monkeypatch):
    """Assert different conditions of user deletion."""
    admin_user = TestUserInfo.user_bcros_active
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    user = factory_user_model(user_info=TestUserInfo.user_bcros_active)
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id, product_code=ProductCode.DIR_SEARCH.value)
    owner_claims = TestJwtClaims.get_test_real_user(user.keycloak_guid)

    patch_token_info(owner_claims, monkeypatch)
    member = TestAnonymousMembership.generate_random_user(USER)
    admin = TestAnonymousMembership.generate_random_user(COORDINATOR)
    membership = [member, admin]
    UserService.create_user_and_add_membership(membership, org.id)
    owner_headers = factory_auth_header(jwt=jwt, claims=owner_claims)
    member_username = IdpHint.BCROS.value + '/' + member['username']
    admin_username = IdpHint.BCROS.value + '/' + admin['username']
    admin_claims = TestJwtClaims.get_test_real_user(uuid.uuid4(), admin_username, access_ype=AccessType.ANONYMOUS.value,
                                                    roles=[Role.ANONYMOUS_USER.value])
    admin_headers = factory_auth_header(jwt=jwt, claims=admin_claims)
    member_claims = TestJwtClaims.get_test_real_user(uuid.uuid4(), member_username,
                                                     access_ype=AccessType.ANONYMOUS.value,
                                                     roles=[Role.ANONYMOUS_USER.value])

    member_headers = factory_auth_header(jwt=jwt, claims=member_claims)

    # set up JWTS for member and admin
    patch_token_info(admin_claims, monkeypatch)
    client.post('/api/v1/users', headers=admin_headers, content_type='application/json',
                data=json.dumps({'isLogin': True}))

    patch_token_info(member_claims, monkeypatch)
    client.post('/api/v1/users', headers=member_headers, content_type='application/json',
                data=json.dumps({'isLogin': True}))

    patch_token_info(owner_claims, monkeypatch)
    # delete only owner ;failure
    rv = client.delete(f"/api/v1/users/{admin_user['username']}", headers=owner_headers,
                       content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED

    # admin trying to delete member: Failure
    patch_token_info(admin_claims, monkeypatch)
    rv = client.delete(f'/api/v1/users/{member_username}', headers=admin_headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED

    # member delete admin: failure
    patch_token_info(member_claims, monkeypatch)
    rv = client.delete(f'/api/v1/users/{admin_username}', headers=member_headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED

    # a self delete ;should work ;mimics leave team for anonymous user
    patch_token_info(member_claims, monkeypatch)
    rv = client.delete(f'/api/v1/users/{member_username}', headers=member_headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT

    patch_token_info(admin_claims, monkeypatch)
    rv = client.delete(f'/api/v1/users/{admin_username}', headers=admin_headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT

    # add one more admin
    patch_token_info(owner_claims, monkeypatch)
    new_owner = TestAnonymousMembership.generate_random_user(ADMIN)
    membership = [new_owner]
    UserService.create_user_and_add_membership(membership, org.id)
    patch_token_info(owner_claims, monkeypatch)
    rv = client.delete(f"/api/v1/users/{IdpHint.BCROS.value + '/' + new_owner['username']}", headers=owner_headers,
                       content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT


def test_add_back_a_delete_bcros(client, jwt, session, keycloak_mock, monkeypatch):
    """Assert different conditions of user deletion."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    user = factory_user_model(user_info=TestUserInfo.user_bcros_active)
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id, product_code=ProductCode.DIR_SEARCH.value)
    owner_claims = TestJwtClaims.get_test_real_user(user.keycloak_guid)
    member = TestAnonymousMembership.generate_random_user(USER)
    membership = [member,
                  TestAnonymousMembership.generate_random_user(COORDINATOR)]
    patch_token_info(owner_claims, monkeypatch)
    UserService.create_user_and_add_membership(membership, org.id)
    headers = factory_auth_header(jwt=jwt, claims=owner_claims)
    member_user_id = IdpHint.BCROS.value + '/' + member.get('username')
    rv = client.delete(f'/api/v1/users/{member_user_id}', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT
    kc_user = KeycloakService.get_user_by_username(member.get('username'))
    assert kc_user.enabled is False
    user_model = UserService.find_by_username(member_user_id)
    assert user_model.as_dict().get('user_status') == UserStatus.INACTIVE.value
    membership = MembershipModel.find_membership_by_userid(user_model.identifier)
    assert membership.status == Status.INACTIVE.value


def test_reset_password(client, jwt, session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an anonymous admin can be Patched."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    user = factory_user_model(user_info=TestUserInfo.user_bcros_active)
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id, product_code=ProductCode.DIR_SEARCH.value)
    owner_claims = TestJwtClaims.get_test_real_user(user.keycloak_guid)
    member = TestAnonymousMembership.generate_random_user(USER)
    admin = TestAnonymousMembership.generate_random_user(COORDINATOR)
    membership = [member, admin]

    patch_token_info(owner_claims, monkeypatch)
    UserService.create_user_and_add_membership(membership, org.id)
    owner_headers = factory_auth_header(jwt=jwt, claims=owner_claims)
    member_username = IdpHint.BCROS.value + '/' + member['username']
    admin_username = IdpHint.BCROS.value + '/' + admin['username']
    admin_claims = TestJwtClaims.get_test_real_user(uuid.uuid4(),
                                                    admin_username,
                                                    access_ype=AccessType.ANONYMOUS.value,
                                                    roles=[Role.ANONYMOUS_USER.value])
    admin_headers = factory_auth_header(jwt=jwt, claims=admin_claims)
    member_claims = TestJwtClaims.get_test_real_user(uuid.uuid4(),
                                                     member_username,
                                                     access_ype=AccessType.ANONYMOUS.value,
                                                     roles=[Role.ANONYMOUS_USER.value])
    member_headers = factory_auth_header(jwt=jwt, claims=member_claims)
    # set up JWTS for member and admin
    patch_token_info(admin_claims, monkeypatch)
    client.post('/api/v1/users', headers=admin_headers, content_type='application/json',
                data=json.dumps({'isLogin': True}))
    patch_token_info(member_claims, monkeypatch)
    client.post('/api/v1/users', headers=member_headers, content_type='application/json',
                data=json.dumps({'isLogin': True}))

    # reset password of admin by owner
    input_data = json.dumps({'username': admin_username, 'password': 'Mysecretcode@1234'})

    patch_token_info(owner_claims, monkeypatch)
    rv = client.patch(f'/api/v1/users/{admin_username}', headers=owner_headers,
                      data=input_data, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT

    # member cant reset password
    patch_token_info(member_claims, monkeypatch)
    rv = client.patch(f'/api/v1/users/{admin_username}', headers=member_headers,
                      data=input_data, content_type='application/json')
    assert rv.status_code == http_status.HTTP_403_FORBIDDEN

    # admin cant reset password
    patch_token_info(admin_claims, monkeypatch)
    rv = client.patch(f'/api/v1/users/{admin_username}', headers=admin_headers,
                      data=input_data, content_type='application/json')
    assert rv.status_code == http_status.HTTP_403_FORBIDDEN


def test_add_user_admin_valid_bcros(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an anonymous admin can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_dir_search_role)
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

    assert rv.status_code == http_status.HTTP_201_CREATED
    assert dictionary['users'][0].get('username') == IdpHint.BCROS.value + '/' + TestUserInfo.user_anonymous_1[
        'username']
    assert dictionary['users'][0].get('password') is None
    assert dictionary['users'][0].get('type') == Role.ANONYMOUS_USER.name
    assert schema_utils.validate(rv.json, 'anonymous_user_response')[0]

    # different error scenarios

    # check expired invitation
    rv = client.post('/api/v1/users/bcros', data=json.dumps(TestUserInfo.user_anonymous_1),
                     headers={'invitation_token': dictionary.get('token')}, content_type='application/json')
    dictionary = json.loads(rv.data)
    assert dictionary['code'] == 'EXPIRED_INVITATION'

    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation_anonymous(org_id=org_id)),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)

    # check duplicate user
    rv = client.post('/api/v1/users/bcros', data=json.dumps(TestUserInfo.user_anonymous_1),
                     headers={'invitation_token': dictionary.get('token')}, content_type='application/json')
    dictionary = json.loads(rv.data)

    assert dictionary['code'] == 409
    assert dictionary['message'] == 'The username is already taken'


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
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv.json, 'user_response')[0]
    user = json.loads(rv.data)
    assert user['firstname'] is not None

    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.updated_test)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv.json, 'user_response')[0]
    user = json.loads(rv.data)
    assert user['firstname'] is not None


def test_update_user_terms_of_use(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a PATCH to an existing user updates that user."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    user = json.loads(rv.data)
    assert user['firstname'] is not None

    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.updated_test)
    input_data = json.dumps({'termsversion': '1', 'istermsaccepted': True})
    rv = client.patch('/api/v1/users/@me', headers=headers,
                      data=input_data, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'user_response')[0]
    user = json.loads(rv.data)
    assert user['userTerms']['termsOfUseAcceptedVersion'] == '1'

    # version 1 is old version ; so api should return terms of service accepted as false
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv.json, 'user_response')[0]
    user = json.loads(rv.data)
    assert user['userTerms']['isTermsOfUseAccepted'] is False


def test_update_user_terms_of_use_invalid_input(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a PATCH to an existing user updates that user."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    user = json.loads(rv.data)
    assert user['firstname'] is not None

    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.updated_test)
    input_data = json.dumps({'invalid': True})
    rv = client.patch('/api/v1/users/@me', headers=headers,
                      data=input_data, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_user_terms_of_use_no_jwt(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a PATCH to an existing user updates that user."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    user = json.loads(rv.data)
    assert user['firstname'] is not None

    # post token with updated claims
    input_data = json.dumps({'invalid': True})
    rv = client.patch('/api/v1/users/@me',
                      data=input_data, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_staff_get_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a staff user can GET a user by id."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # GET the test user as a staff user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/users/{}'.format(TestJwtClaims.public_user_role['preferred_username']),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'user_response')[0]
    user = json.loads(rv.data)
    assert user['firstname'] is not None


def test_staff_get_user_invalid_id_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a staff user can GET a user by id."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/users/{}'.format('SOME_USER'), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_staff_search_users(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a staff user can GET a list of users with search parameters."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # POST a second test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.no_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # Search on all users as a staff user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'users_response')[0]
    users = json.loads(rv.data)
    assert len(users) == 2

    # Search on users with a search parameter
    rv = client.get('/api/v1/users?lastname={}'.format(TestJwtClaims.no_role['lastname']),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'users_response')[0]
    users = json.loads(rv.data)
    assert len(users) == 1


def test_get_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user can retrieve their own profile."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    rv = client.get('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'user_response')[0]
    user = json.loads(rv.data)
    assert user['firstname'] is not None


def test_get_user_returns_401(client, session):  # pylint:disable=unused-argument
    """Assert that unauthorized access to a user profile returns a 401 error."""
    rv = client.get('/api/v1/users/@me', headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_get_user_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the endpoint returns 404 when user is not found."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == Error.DATA_NOT_FOUND.status_code


def test_add_contact(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a contact can be added (POST) to an existing user."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # POST a contact to test user
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv.json, 'contact_response')[0]
    contact = json.loads(rv.data)
    assert contact['email'] == 'foo@bar.com'


def test_add_contact_valid_email_with_special_characters(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a contact can be added (POST) to an existing user."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
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
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.invalid),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_contact_duplicate_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact for a user who already has a contact returns a 400."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
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
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # POST a contact to test user
    rv = client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # PUT a contact on the same user
    rv = client.put('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact2),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'contact_response')[0]
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
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.put('/api/v1/users/contacts', data=json.dumps(TestContactInfo.invalid),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact_missing_contact_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating a contact for a non-existent user returns a 404."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # PUT a contact to test user
    rv = client.put('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact1),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_delete_contact(client, jwt, session):  # pylint:disable=unused-argument, invalid-name
    """Assert that a contact can be deleted on an existing user."""
    # POST a test user
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
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
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.delete('/api/v1/users/contacts', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_get_orgs_for_user(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that retrieving a list of orgs for a user functions."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    # Add an org - the current user should be auto-added as an ADMIN
    rv = client.post('/api/v1/orgs', headers=headers, data=json.dumps(TestOrgInfo.org1),
                     content_type='application/json')

    rv = client.get('/api/v1/users/orgs', headers=headers)

    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'orgs_response')[0]

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

    claims = copy.deepcopy(TestJwtClaims.public_user_role.value)
    claims['sub'] = str(user.keycloak_guid)

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get('/api/v1/users/authorizations', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('authorizations')[0].get('orgMembership') == 'ADMIN'

    # Test with invalid user
    claims['sub'] = str(uuid.uuid4())
    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get('/api/v1/users/authorizations', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert len(rv.json.get('authorizations')) == 0


def test_delete_user_with_no_orgs_returns_204(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Test if the user doesn't have any teams/orgs assert status is 204."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # post token with updated claims
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.updated_test)

    rv = client.delete('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT


def test_delete_inactive_user_returns_400(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Test if the user doesn't have any teams/orgs assert status is 204."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
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


def test_delete_user_as_only_admin_returns_400(client, jwt, session, keycloak_mock,
                                               monkeypatch):  # pylint:disable=unused-argument
    """Test if the user is the only owner of a team assert status is 400."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.commit()

    claims = copy.deepcopy(TestJwtClaims.public_user_role.value)
    claims['sub'] = str(user_model.keycloak_guid)

    patch_token_info(claims, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user_model.id)
    org_dictionary = org.as_dict()
    org_id = org_dictionary['id']

    entity = factory_entity_model(entity_info=TestEntityInfo.entity_lear_mock)

    affiliation = AffiliationModel(org_id=org_id, entity_id=entity.id)
    affiliation.save()

    headers = factory_auth_header(jwt=jwt, claims=claims)

    rv = client.delete('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_delete_user_is_member_returns_204(client, jwt, session, keycloak_mock,
                                           monkeypatch):  # pylint:disable=unused-argument
    """Test if the user is the member of a team assert status is 204."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.commit()

    user_model2 = factory_user_model(user_info=TestUserInfo.user2)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model2
    contact_link.commit()

    claims = copy.deepcopy(TestJwtClaims.public_user_role.value)
    claims['sub'] = str(user_model2.keycloak_guid)

    patch_token_info(claims, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org1, user_id=user_model.id)
    org_dictionary = org.as_dict()
    org_id = org_dictionary['id']

    entity = factory_entity_model(entity_info=TestEntityInfo.entity_lear_mock)
    affiliation = AffiliationModel(org_id=org_id, entity_id=entity.id)
    affiliation.save()

    membership = MembershipModel(org_id=org_id, user_id=user_model2.id, membership_type_code='USER',
                                 membership_type_status=Status.ACTIVE.value)
    membership.save()

    headers = factory_auth_header(jwt=jwt, claims=claims)

    rv = client.delete('/api/v1/users/@me', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT


def test_delete_otp_for_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user can be POSTed."""
    # ADMIN
    admin_user = factory_user_model(user_info=TestUserInfo.user1)
    org = factory_org_model(org_info=TestOrgInfo.org_regular_bceid)
    factory_membership_model(admin_user.id, org.id)
    admin_claims = TestJwtClaims.get_test_real_user(admin_user.keycloak_guid)
    admin_headers = factory_auth_header(jwt=jwt, claims=admin_claims)

    # COORDINATOR
    coordinator_user = factory_user_model(user_info=TestUserInfo.user2)
    factory_membership_model(coordinator_user.id, org.id, member_type=COORDINATOR)
    coordinator_claims = TestJwtClaims.get_test_real_user(coordinator_user.keycloak_guid)
    coordinator_headers = factory_auth_header(jwt=jwt, claims=coordinator_claims)

    # just a member
    member_user = factory_user_model(user_info=TestUserInfo.user3)
    factory_membership_model(member_user.id, org.id, member_type=USER)
    user_claims = TestJwtClaims.get_test_real_user(member_user.keycloak_guid)
    user_headers = factory_auth_header(jwt=jwt, claims=user_claims)

    request = KeycloakScenario.create_user_by_user_info(user_info=TestJwtClaims.tester_bceid_role)
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    assert 'CONFIGURE_TOTP' not in json.loads(user.value()).get('requiredActions', None)
    user_id = user.id
    # Create user, org and membserhip in DB
    user = factory_user_model(TestUserInfo.get_bceid_user_with_kc_guid(user_id))
    factory_membership_model(user.id, org.id)

    # staff with manage accounts otp reset
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.delete(f'api/v1/users/{user.username}/otp', headers=headers)
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT

    user1 = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)

    assert 'CONFIGURE_TOTP' in json.loads(user1.value()).get('requiredActions')

    # staff with basic access cant do otp reset
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.delete(f'api/v1/users/{user.username}/otp', headers=headers)
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED

    #  admin can do otp reset
    rv = client.delete(f'api/v1/users/{user.username}/otp', headers=admin_headers)
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT

    #  coordinator can do otp reset
    rv = client.delete(f'api/v1/users/{user.username}/otp', headers=coordinator_headers)
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT

    #  user can not do otp reset
    rv = client.delete(f'api/v1/users/{user.username}/otp', headers=user_headers)
    assert rv.status_code == http_status.HTTP_403_FORBIDDEN

    # another org admin cant do
    admin_user1 = factory_user_model(user_info=TestUserInfo.user_test)
    org1 = factory_org_model(org_info=TestOrgInfo.org2, org_type_info=TestOrgTypeInfo.implicit)
    factory_membership_model(admin_user1.id, org1.id)
    admin_claims = TestJwtClaims.get_test_real_user(admin_user1.keycloak_guid)
    admin1_headers = factory_auth_header(jwt=jwt, claims=admin_claims)
    rv = client.delete(f'api/v1/users/{user.username}/otp', headers=admin1_headers)
    assert rv.status_code == http_status.HTTP_403_FORBIDDEN


def test_add_bceid_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user can be POSTed."""
    # Create a user in keycloak
    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.get_test_user(user_id, source='BCEID'))
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json', data=json.dumps({
        'firstName': 'John',
        'lastName': 'Doe'
    }))
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert rv.json.get('firstname') == 'John'

    rv = client.post('/api/v1/users', headers=headers, content_type='application/json', data=json.dumps({
        'firstName': 'John-New',
        'lastName': 'Doe'
    }))

    assert rv.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv.json, 'user_response')[0]
    assert rv.json.get('firstname') == 'John-New'


def test_user_post_during_login(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user can be POSTed."""
    # Create a user by POST, then create same user with login flag and make sure the login date is different
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    login_time = rv.json.get('loginTime')
    # Call the same endpoint again and confirm logn time is same
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert login_time == rv.json.get('loginTime')

    # Call same endpoint with login flag and assert login time is different
    time.sleep(1)
    rv = client.post('/api/v1/users', headers=headers, data=json.dumps({'isLogin': True}),
                     content_type='application/json')
    assert schema_utils.validate(rv.json, 'user_response')[0]
    assert login_time != rv.json.get('loginTime')


def test_get_affidavit(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert get affidavit."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post('/api/v1/users', headers=headers, content_type='application/json')

    document_signature = client.get('/api/v1/documents/test.jpeg/signatures', headers=headers,
                                    content_type='application/json')
    doc_key = document_signature.json.get('key')
    client.post(f"/api/v1/users/{TestJwtClaims.public_user_role.get('sub')}/affidavits",
                headers=headers,
                data=json.dumps(TestAffidavit.get_test_affidavit_with_contact(doc_id=doc_key)),
                content_type='application/json')

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)

    rv = client.get(f"/api/v1/users/{TestJwtClaims.public_user_role.get('sub')}/affidavits",
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK

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

"""Tests to verify the User Service.

Test-Suite to ensure that the User Service is working as expected.
"""
from unittest.mock import patch

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import User as UserModel
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.constants import IdpHint
from auth_api.utils.roles import Status, ADMIN, OWNER, MEMBER
from werkzeug.exceptions import HTTPException

from tests.utilities.factory_scenarios import TestContactInfo, TestEntityInfo, TestJwtClaims, TestOrgInfo, \
    TestUserInfo, TestAnonymousMembership, KeycloakScenario
from tests.utilities.factory_utils import factory_contact_model, factory_entity_model, factory_user_model, \
    factory_org_model, factory_membership_model


def test_as_dict(session):  # pylint: disable=unused-argument
    """Assert that a user is rendered correctly as a dictionary."""
    user_model = factory_user_model()
    user = UserService(user_model)

    dictionary = user.as_dict()
    assert dictionary['username'] == TestUserInfo.user1['username']
    assert dictionary['roles'] == TestUserInfo.user1['roles']


def test_user_save_by_token(session):  # pylint: disable=unused-argument
    """Assert that a user can be created by token."""
    user = UserService.save_from_jwt_token(TestJwtClaims.user_test)
    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['username'] == TestJwtClaims.user_test['preferred_username']
    assert dictionary['keycloakGuid'] == TestJwtClaims.user_test['sub']


def test_bcros_user_save_by_token(session):  # pylint: disable=unused-argument
    """Assert that a user can be created by token."""
    user = UserService.save_from_jwt_token(TestJwtClaims.anonymous_bcros_role)
    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['username'] == TestJwtClaims.anonymous_bcros_role['preferred_username']
    assert dictionary['keycloakGuid'] == TestJwtClaims.anonymous_bcros_role['sub']


def test_bcros_user_update_by_token(session):  # pylint: disable=unused-argument
    """Assert that a user can be created by token."""
    user_model = factory_user_model(TestUserInfo.user_bcros)
    user = UserService(user_model)
    dictionary = user.as_dict()
    assert dictionary.get('keycloakGuid', None) is None

    user = UserService.save_from_jwt_token(TestJwtClaims.anonymous_bcros_role)
    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['username'] == TestJwtClaims.anonymous_bcros_role['preferred_username']
    assert dictionary['keycloakGuid'] == TestJwtClaims.anonymous_bcros_role['sub']


def test_user_save_by_token_no_token(session):  # pylint: disable=unused-argument
    """Assert that a user cannot be created from an empty token."""
    user = UserService.save_from_jwt_token(None)
    assert user is None


def test_create_user_and_add_membership_owner_skip_auth_mode(session, auth_mock,
                                                             keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an owner can be added as anonymous."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    membership = [TestAnonymousMembership.generate_random_user(OWNER)]
    users = UserService.create_user_and_add_membership(membership, org.id, single_mode=True)
    assert len(users['users']) == 1
    assert users['users'][0]['username'] == IdpHint.BCROS.value + '/' + membership[0]['username']
    assert users['users'][0]['type'] == 'ANONYMOUS'

    members = MembershipModel.find_members_by_org_id(org.id)

    # only one member should be there since its a STAFF created org
    assert len(members) == 1
    assert members[0].membership_type_code == OWNER


def test_create_user_and_add_same_user_name_error_in_kc(session, auth_mock,
                                                        keycloak_mock):  # pylint:disable=unused-argument
    """Assert that same user name cannot be added twice."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    membership = [TestAnonymousMembership.generate_random_user(OWNER)]
    keycloak_service = KeycloakService()
    request = KeycloakScenario.create_user_request()
    request.user_name = membership[0]['username']
    keycloak_service.add_user(request)
    users = UserService.create_user_and_add_membership(membership, org.id, single_mode=True)
    assert users['users'][0]['http_status'] == 409
    assert users['users'][0]['error'] == 'The username is already taken'


def test_create_user_and_add_same_user_name_error_in_db(session, auth_mock,
                                                        keycloak_mock):  # pylint:disable=unused-argument
    """Assert that same user name cannot be added twice."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    user = factory_user_model(TestUserInfo.user_bcros)
    factory_membership_model(user.id, org.id)
    new_members = TestAnonymousMembership.generate_random_user(OWNER)
    new_members['username'] = user.username.replace(f'{IdpHint.BCROS.value}/', '')
    membership = [new_members]
    users = UserService.create_user_and_add_membership(membership, org.id, single_mode=True)
    assert users['users'][0]['http_status'] == 409
    assert users['users'][0]['error'] == 'The username is already taken'


def test_create_user_and_add_transaction_membership(session
                                                    , auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an owner can be added as anonymous."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    membership = [TestAnonymousMembership.generate_random_user(OWNER)]
    with patch('auth_api.models.Membership.save', side_effect=Exception('mocked error')):
        users = UserService.create_user_and_add_membership(membership, org.id, single_mode=True)

    user_name = IdpHint.BCROS.value + '/' + membership[0]['username']
    assert len(users['users']) == 1
    assert users['users'][0]['username'] == membership[0]['username']
    assert users['users'][0]['http_status'] == 500
    assert users['users'][0]['error'] == 'Adding User Failed'

    # make sure no records are created
    user = UserModel.find_by_username(user_name)
    assert user is None
    user = UserModel.find_by_username(membership[0]['username'])
    assert user is None
    members = MembershipModel.find_members_by_org_id(org.id)
    # only one member should be there since its a STAFF created org
    assert len(members) == 0


def test_create_user_and_add_membership_admin_skip_auth_mode(session, auth_mock,
                                                             keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an admin can be added as anonymous."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    membership = [TestAnonymousMembership.generate_random_user(ADMIN)]
    users = UserService.create_user_and_add_membership(membership, org.id, single_mode=True)
    assert len(users['users']) == 1
    assert users['users'][0]['username'] == IdpHint.BCROS.value + '/' + membership[0]['username']
    assert users['users'][0]['type'] == 'ANONYMOUS'

    members = MembershipModel.find_members_by_org_id(org.id)

    # only one member should be there since its a STAFF created org
    assert len(members) == 1
    assert members[0].membership_type_code == ADMIN


def test_create_user_and_add_membership_admin_bulk_mode(session, auth_mock,
                                                        keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an admin can add a member."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    user = factory_user_model()
    factory_membership_model(user.id, org.id)
    claims = TestJwtClaims.get_test_real_user(user.keycloak_guid)
    membership = [TestAnonymousMembership.generate_random_user(MEMBER)]
    users = UserService.create_user_and_add_membership(membership, org.id, token_info=claims)

    assert len(users['users']) == 1
    assert users['users'][0]['username'] == IdpHint.BCROS.value + '/' + membership[0]['username']
    assert users['users'][0]['type'] == 'ANONYMOUS'

    members = MembershipModel.find_members_by_org_id(org.id)

    # staff didnt create members..so count is count of owner+other 1 member
    assert len(members) == 2


def test_create_user_and_add_membership_admin_bulk_mode_unauthorised(session, auth_mock,
                                                                     keycloak_mock):  # pylint:disable=unused-argument
    """Assert that bulk operation cannot be performed by unauthorised users."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    user = factory_user_model()
    factory_membership_model(user.id, org.id)
    membership = [TestAnonymousMembership.generate_random_user(MEMBER)]

    with pytest.raises(HTTPException) as excinfo:
        UserService.create_user_and_add_membership(membership, org.id, token_info=TestJwtClaims.public_user_role)
    assert excinfo.value.code == 403


def test_create_user_and_add_membership_admin_bulk_mode_multiple(session, auth_mock,
                                                                 keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an admin can add a group of members."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    user = factory_user_model()
    factory_membership_model(user.id, org.id)
    claims = TestJwtClaims.get_test_real_user(user.keycloak_guid)
    membership = [TestAnonymousMembership.generate_random_user(MEMBER),
                  TestAnonymousMembership.generate_random_user(ADMIN)]
    users = UserService.create_user_and_add_membership(membership, org.id, token_info=claims)

    assert len(users['users']) == 2
    assert users['users'][0]['username'] == IdpHint.BCROS.value + '/' + membership[0]['username']
    assert users['users'][0]['type'] == 'ANONYMOUS'
    assert users['users'][1]['username'] == IdpHint.BCROS.value + '/' + membership[1]['username']
    assert users['users'][1]['type'] == 'ANONYMOUS'

    members = MembershipModel.find_members_by_org_id(org.id)

    # staff didnt create members..so count is count of owner+other 2 members
    assert len(members) == 3


def test_create_user_and_add_membership_member_error_skip_auth_mode(session, auth_mock,
                                                                    keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an member cannot be added as anonymous in single_mode mode."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    membership = [TestAnonymousMembership.generate_random_user(MEMBER)]
    with pytest.raises(BusinessException) as exception:
        UserService.create_user_and_add_membership(membership, org.id,
                                                   single_mode=True)
    assert exception.value.code == Error.INVALID_USER_CREDENTIALS.name


def test_create_user_and_add_membership_multiple_error_skip_auth_mode(session, auth_mock,
                                                                      keycloak_mock):  # pylint:disable=unused-argument
    """Assert that multiple user cannot be created  in single_mode mode."""
    org = factory_org_model(org_info=TestOrgInfo.org_anonymous)
    membership = [TestAnonymousMembership.generate_random_user(MEMBER),
                  TestAnonymousMembership.generate_random_user(ADMIN)]
    with pytest.raises(BusinessException) as exception:
        UserService.create_user_and_add_membership(membership, org.id, TestJwtClaims.public_user_role,
                                                   single_mode=True)
    assert exception.value.code == Error.INVALID_USER_CREDENTIALS.name


def test_user_save_by_token_fail(session):  # pylint: disable=unused-argument
    """Assert that a user cannot not be created."""
    with patch.object(UserModel, 'create_from_jwt_token', return_value=None):
        user = UserService.save_from_jwt_token(TestJwtClaims.user_test)
        assert user is None


def test_add_contact_to_user(session):  # pylint: disable=unused-argument
    """Assert that a contact can be added to a user."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.user_test['sub']
    factory_user_model(user_info=user_with_token)

    contact = UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact1).as_dict()

    assert contact['email'] == TestContactInfo.contact1['email']
    assert contact['phone'] == TestContactInfo.contact1['phone']
    assert contact['phoneExtension'] == TestContactInfo.contact1['phoneExtension']


def test_add_contact_user_no_user(session):  # pylint: disable=unused-argument
    """Assert that a contact cannot be added to a user that does not exist."""
    with pytest.raises(BusinessException) as exception:
        UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact1)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_add_contact_to_user_already_exists(session):  # pylint: disable=unused-argument
    """Assert that a contact cannot be added to a user that already has a contact."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.user_test['sub']
    factory_user_model(user_info=user_with_token)

    UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact1)

    with pytest.raises(BusinessException) as exception:
        UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact2)
    assert exception.value.code == Error.DATA_ALREADY_EXISTS.name


def test_update_contact_for_user(session):  # pylint: disable=unused-argument
    """Assert that a contact can be updated for a user."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.user_test['sub']
    factory_user_model(user_info=user_with_token)

    contact = UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact1).as_dict()

    assert contact is not None

    updated_contact = UserService.update_contact(TestJwtClaims.user_test, TestContactInfo.contact2).as_dict()

    assert updated_contact is not None
    assert updated_contact['email'] == TestContactInfo.contact2['email']


def test_update_terms_of_use_for_user(session):  # pylint: disable=unused-argument
    """Assert that a terms of use can be updated for a user."""
    UserService.save_from_jwt_token(TestJwtClaims.user_test)

    updated_user = UserService.update_terms_of_use(TestJwtClaims.user_test, True, 1)
    dictionary = updated_user.as_dict()
    assert dictionary['userTerms']['isTermsOfUseAccepted'] is True


def test_update_contact_for_user_no_user(session):  # pylint: disable=unused-argument
    """Assert that a contact cannot be updated for a user that does not exist."""
    with pytest.raises(BusinessException) as exception:
        UserService.update_contact(TestJwtClaims.user_test, TestContactInfo.contact2)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_update_contact_for_user_no_contact(session):  # pylint: disable=unused-argument
    """Assert that a contact cannot be updated for a user with no contact."""
    factory_user_model(user_info=TestUserInfo.user_test)

    with pytest.raises(BusinessException) as exception:
        UserService.update_contact(TestJwtClaims.user_test, TestContactInfo.contact2)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_delete_contact_for_user(session):  # pylint: disable=unused-argument
    """Assert that a contact can be deleted for a user."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.user_test['sub']
    factory_user_model(user_info=user_with_token)

    contact = UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact1).as_dict()

    assert contact is not None

    deleted_contact = UserService.delete_contact(TestJwtClaims.user_test).as_dict()

    assert deleted_contact is not None

    contacts = UserService.get_contacts(TestJwtClaims.user_test)
    assert contacts.get('contacts') == []


def test_delete_contact_for_user_no_user(session):  # pylint: disable=unused-argument
    """Assert that deleting a contact for a non-existent user raises the right exception."""
    with pytest.raises(BusinessException) as exception:
        UserService.delete_contact(TestJwtClaims.user_test)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_delete_contact_for_user_no_contact(session):  # pylint: disable=unused-argument
    """Assert that deleting a contact for a user with no contact raises the right exception."""
    factory_user_model(user_info=TestUserInfo.user_test)

    with pytest.raises(BusinessException) as exception:
        UserService.delete_contact(TestJwtClaims.user_test)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_find_users(session):  # pylint: disable=unused-argument
    """Assert that a list of users can be retrieved and searched on."""
    factory_user_model()

    factory_user_model(user_info=TestUserInfo.user2)

    users = UserService.find_users(last_name='User')
    assert users is not None
    assert len(users) == 2


def test_user_find_by_token(session):  # pylint: disable=unused-argument
    """Assert that a user can be found by token."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.user_test['sub']
    factory_user_model(user_info=user_with_token)

    found_user = UserService.find_by_jwt_token(None)
    assert found_user is None

    found_user = UserService.find_by_jwt_token(TestJwtClaims.user_test)
    assert found_user is not None
    dictionary = found_user.as_dict()
    assert dictionary['username'] == TestJwtClaims.user_test['preferred_username']
    assert dictionary['keycloakGuid'] == TestJwtClaims.user_test['sub']


def test_user_find_by_username(session):  # pylint: disable=unused-argument
    """Assert that a user can be found by username."""
    user_model = factory_user_model()
    user = UserService(user_model)

    user = UserService.find_by_username(None)
    assert user is None

    user = UserService.find_by_username(TestUserInfo.user_test['username'])

    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['username'] == TestUserInfo.user_test['username']


def test_user_find_by_username_no_model_object(session):  # pylint: disable=unused-argument
    """Assert that the business can't be found with no model."""
    username = TestUserInfo.user_test['username']

    user = UserService.find_by_username(username)

    assert user is None


def test_user_find_by_username_missing_username(session):  # pylint: disable=unused-argument
    """Assert that the business can't be found by incorrect username."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    user = UserService(user_model)

    user = UserService.find_by_username('foo')

    assert user is None


def test_delete_contact_user_link(session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a contact can not be deleted if contact link exists."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user_model = factory_user_model(user_info=user_with_token)
    user = UserService(user_model)

    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.identifier)
    org_dictionary = org.as_dict()
    org_id = org_dictionary['id']

    contact = factory_contact_model()

    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.org = org._model  # pylint:disable=protected-access
    contact_link = contact_link.flush()
    contact_link.commit()

    deleted_contact = UserService.delete_contact(TestJwtClaims.public_user_role)

    assert deleted_contact is None

    delete_contact_link = ContactLinkModel.find_by_user_id(user.identifier)
    assert not delete_contact_link

    exist_contact_link = ContactLinkModel.find_by_org_id(org_id)
    assert exist_contact_link


def test_delete_user(session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a user can be deleted."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.user_test['sub']
    user_model = factory_user_model(user_info=user_with_token)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.commit()

    org = OrgService.create_org(TestOrgInfo.org1, user_id=user_model.id)

    UserService.delete_user(TestJwtClaims.user_test)
    updated_user = UserModel.find_by_jwt_token(TestJwtClaims.user_test)
    assert len(updated_user.contacts) == 0

    user_orgs = MembershipModel.find_orgs_for_user(updated_user.id)
    for org in user_orgs:
        assert org.status_code == 'INACTIVE'


def test_delete_user_where_org_has_affiliations(session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a user can be deleted."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link = contact_link.flush()
    contact_link.commit()

    org = OrgService.create_org(TestOrgInfo.org1, user_id=user_model.id).as_dict()
    org_id = org['id']

    entity = factory_entity_model(entity_info=TestEntityInfo.entity_lear_mock)

    affiliation = AffiliationModel(org_id=org_id, entity_id=entity.id)
    affiliation.save()
    with pytest.raises(BusinessException) as exception:
        UserService.delete_user(TestJwtClaims.user_test)
        assert exception.code == Error.DELETE_FAILED_ONLY_OWNER

    updated_user = UserModel.find_by_jwt_token(TestJwtClaims.user_test)
    contacts = UserService.get_contacts(TestJwtClaims.user_test)
    assert len(contacts) == 1

    user_orgs = MembershipModel.find_orgs_for_user(updated_user.id)
    for org in user_orgs:
        assert org.status_code == 'ACTIVE'


def test_delete_user_where_user_is_member_on_org(session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a user can be deleted."""
    # Create a user and org
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

    # Create another user and add membership to the above org
    user_model2 = factory_user_model(user_info=TestUserInfo.user2)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model2
    contact_link.commit()

    membership = MembershipModel(org_id=org_id, user_id=user_model2.id, membership_type_code='MEMBER',
                                 membership_type_status=Status.ACTIVE.value)
    membership.save()

    UserService.delete_user(TestJwtClaims.get_test_user(user_model2.keycloak_guid))

    updated_user = UserModel.find_by_jwt_token(TestJwtClaims.get_test_user(user_model2.keycloak_guid))
    assert len(updated_user.contacts) == 0

    user_orgs = MembershipModel.find_orgs_for_user(updated_user.id)
    for org in user_orgs:
        assert org.status_code == 'INACTIVE'


def test_delete_user_where_org_has_another_owner(session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a user can be deleted."""
    # Create a user and org
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

    # Create another user and add membership to the above org
    user_model2 = factory_user_model(user_info=TestUserInfo.user2)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model2
    contact_link.commit()

    membership = MembershipModel(org_id=org_id, user_id=user_model2.id, membership_type_code='OWNER',
                                 membership_type_status=Status.ACTIVE.value)
    membership.save()
    membership.commit()

    # with pytest.raises(BusinessException) as exception:
    UserService.delete_user(TestJwtClaims.get_test_user(user_model2.keycloak_guid))

    updated_user = UserModel.find_by_jwt_token(TestJwtClaims.get_test_user(user_model2.keycloak_guid))
    assert len(updated_user.contacts) == 0

    user_orgs = MembershipModel.find_orgs_for_user(updated_user.id)
    for org in user_orgs:
        assert org.status_code == 'INACTIVE'

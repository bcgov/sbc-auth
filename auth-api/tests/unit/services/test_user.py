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
from auth_api.utils.roles import Status
from tests.utilities.factory_scenarios import TestContactInfo, TestEntityInfo, TestJwtClaims, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import factory_contact_model, factory_entity_model, factory_user_model


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


def test_user_save_by_token_no_token(session):  # pylint: disable=unused-argument
    """Assert that a user cannot be created from an empty token."""
    user = UserService.save_from_jwt_token(None)
    assert user is None


def test_user_save_by_token_fail(session):  # pylint: disable=unused-argument
    """Assert that a user cannot not be created."""
    with patch.object(UserModel, 'create_from_jwt_token', return_value=None):
        user = UserService.save_from_jwt_token(TestJwtClaims.user_test)
        assert user is None


def test_add_contact_to_user(session):  # pylint: disable=unused-argument
    """Assert that a contact can be added to a user."""
    factory_user_model(user_info=TestUserInfo.user_test)

    user = UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact1)

    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['contacts']
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TestContactInfo.contact1['email']
    assert dictionary['contacts'][0]['phone'] == TestContactInfo.contact1['phone']
    assert dictionary['contacts'][0]['phoneExtension'] == TestContactInfo.contact1['phoneExtension']


def test_add_contact_user_no_user(session):  # pylint: disable=unused-argument
    """Assert that a contact cannot be added to a user that does not exist."""
    with pytest.raises(BusinessException) as exception:
        UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact1)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_add_contact_to_user_already_exists(session):  # pylint: disable=unused-argument
    """Assert that a contact cannot be added to a user that already has a contact."""
    factory_user_model(user_info=TestUserInfo.user_test)

    UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact1)

    with pytest.raises(BusinessException) as exception:
        UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact2)
    assert exception.value.code == Error.DATA_ALREADY_EXISTS.name


def test_update_contact_for_user(session):  # pylint: disable=unused-argument
    """Assert that a contact can be updated for a user."""
    factory_user_model(user_info=TestUserInfo.user_test)

    user = UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact1)

    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['contacts']
    assert len(dictionary['contacts']) == 1

    updated_user = UserService.update_contact(TestJwtClaims.user_test, TestContactInfo.contact2)

    assert updated_user is not None
    dictionary = updated_user.as_dict()
    assert dictionary['contacts'][0]['email'] == TestContactInfo.contact2['email']


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
    factory_user_model(user_info=TestUserInfo.user_test)

    user = UserService.add_contact(TestJwtClaims.user_test, TestContactInfo.contact1)

    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['contacts']
    assert len(dictionary['contacts']) == 1

    updated_user = UserService.delete_contact(TestJwtClaims.user_test)

    assert updated_user is not None
    dictionary = updated_user.as_dict()
    assert dictionary.get('contacts') == []


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
    factory_user_model(user_info=TestUserInfo.user_test)

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


def test_delete_contact_user_link(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that a contact can not be deleted if contact link exists."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    user = UserService(user_model)

    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.identifier)
    org_dictionary = org.as_dict()
    org_id = org_dictionary['id']

    contact = factory_contact_model()

    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.org = org._model  # pylint:disable=protected-access
    contact_link.commit()

    updated_user = user.delete_contact(TestJwtClaims.user_test)

    dictionary = None
    dictionary = updated_user.as_dict()
    assert len(dictionary['contacts']) == 0

    delete_contact_link = ContactLinkModel.find_by_user_id(user.identifier)
    assert not delete_contact_link

    exist_contact_link = ContactLinkModel.find_by_org_id(org_id)
    assert exist_contact_link


def test_delete_user(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that a user can be deleted."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
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


def test_delete_user_where_org_has_affiliations(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that a user can be deleted."""
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
    with pytest.raises(BusinessException) as exception:
        UserService.delete_user(TestJwtClaims.user_test)
        assert exception.code == Error.DELETE_FAILED_ONLY_OWNER

    updated_user = UserModel.find_by_jwt_token(TestJwtClaims.user_test)
    assert len(updated_user.contacts) == 1

    user_orgs = MembershipModel.find_orgs_for_user(updated_user.id)
    for org in user_orgs:
        assert org.status_code == 'ACTIVE'


def test_delete_user_where_user_is_member_on_org(session, auth_mock):  # pylint:disable=unused-argument
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


def test_delete_user_where_org_has_another_owner(session, auth_mock):  # pylint:disable=unused-argument
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

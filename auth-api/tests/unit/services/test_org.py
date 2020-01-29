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
"""Tests for the Org service.

Test suite to ensure that the Org service routines are working as expected.
"""
from unittest.mock import patch

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.services import Invitation as InvitationService
from auth_api.services import Membership as MembershipService
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService
from auth_api.services.entity import Entity as EntityService
from tests.utilities.factory_scenarios import TestContactInfo, TestJwtClaims, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import (
    factory_contact_model, factory_entity_model, factory_invitation, factory_membership_model, factory_org_service,
    factory_user_model)


def test_as_dict(session):  # pylint:disable=unused-argument
    """Assert that the Org is exported correctly as a dictinoary."""
    org = factory_org_service()

    dictionary = org.as_dict()
    assert dictionary
    assert dictionary['name'] == TestOrgInfo.org1['name']


def test_create_org(session):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model()
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org1['name']


def test_update_org(session):  # pylint:disable=unused-argument
    """Assert that an Org can be updated."""
    org = factory_org_service()

    org.update_org(TestOrgInfo.org2)

    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org2['name']


def test_update__duplicate_org(session):  # pylint:disable=unused-argument
    """Assert that an Org cannot be updated."""
    org = factory_org_service()

    org.update_org(TestOrgInfo.org2)

    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org2['name']

    with pytest.raises(BusinessException) as exception:
        org.update_org(TestOrgInfo.org2)
    assert exception.value.code == Error.DATA_CONFLICT.name


def test_find_org_by_id(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an org can be retrieved by its id."""
    org = factory_org_service()
    dictionary = org.as_dict()
    org_id = dictionary['id']

    found_org = OrgService.find_by_org_id(org_id)
    assert found_org
    dictionary = found_org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org1['name']


def test_find_org_by_id_no_org(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an org which does not exist cannot be retrieved."""
    org = OrgService.find_by_org_id(99)
    assert org is None


def test_add_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an org."""
    org = factory_org_service()
    org_dictionary = org.as_dict()
    contact = OrgService.add_contact(org_dictionary['id'], TestContactInfo.contact1)
    dictionary = contact.as_dict()
    assert dictionary['email'] == TestContactInfo.contact1['email']


def test_add_contact_duplicate(session):  # pylint:disable=unused-argument
    """Assert that a contact cannot be added to an Org if that Org already has a contact."""
    org = factory_org_service()
    org_dictionary = org.as_dict()
    OrgService.add_contact(org_dictionary['id'], TestContactInfo.contact1)

    with pytest.raises(BusinessException) as exception:
        OrgService.add_contact(org_dictionary['id'], TestContactInfo.contact2)
    assert exception.value.code == Error.DATA_ALREADY_EXISTS.name


def test_update_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact for an existing Org can be updated."""
    org = factory_org_service()
    org_dictionary = org.as_dict()
    contact = OrgService.add_contact(org_dictionary['id'], TestContactInfo.contact1)
    dictionary = contact.as_dict()

    assert dictionary['email'] == TestContactInfo.contact1['email']

    updated_contact = OrgService.update_contact(org_dictionary['id'], TestContactInfo.contact2)
    dictionary = updated_contact.as_dict()

    assert dictionary['email'] == TestContactInfo.contact2['email']


def test_update_contact_no_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact for a non-existent contact cannot be updated."""
    org = factory_org_service()
    org_dictionary = org.as_dict()

    with pytest.raises(BusinessException) as exception:
        OrgService.update_contact(org_dictionary['id'], TestContactInfo.contact2)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_get_members(session):  # pylint:disable=unused-argument
    """Assert that members for an org can be retrieved."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.edit_role['sub']
    user = factory_user_model(user_info=user_with_token)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    org_dictionary = org.as_dict()

    response = MembershipService.get_members_for_org(org_dictionary['id'],
                                                     status='ACTIVE',
                                                     token_info=TestJwtClaims.edit_role)
    assert response
    assert len(response) == 1
    assert response[0].membership_type_code == 'OWNER'


def test_get_invitations(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that invitations for an org can be retrieved."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        user_with_token = TestUserInfo.user_test
        user_with_token['keycloak_guid'] = TestJwtClaims.edit_role['sub']
        user = factory_user_model(user_info=user_with_token)
        org = OrgService.create_org(TestOrgInfo.org1, user.id)
        org_dictionary = org.as_dict()

        invitation_info = factory_invitation(org_dictionary['id'])

        invitation = InvitationService.create_invitation(invitation_info, UserService(user), {}, '')

        response = InvitationService.get_invitations_for_org(org_dictionary['id'], 'PENDING', TestJwtClaims.edit_role)
        assert response
        assert len(response) == 1
        assert response[0].recipient_email == invitation.as_dict()['recipientEmail']


def test_get_owner_count_one_owner(session):  # pylint:disable=unused-argument
    """Assert that count of owners is correct."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.edit_role['sub']
    user = factory_user_model(user_info=user_with_token)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    assert org.get_owner_count() == 1


def test_get_owner_count_two_owner_with_admins(session):  # pylint:disable=unused-argument
    """Assert that count of owners is correct."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.edit_role['sub']
    user = factory_user_model(user_info=user_with_token)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    user2 = factory_user_model(user_info=TestUserInfo.user2)
    factory_membership_model(user2.id, org._model.id, member_type='ADMIN')
    user3 = factory_user_model(user_info=TestUserInfo.user3)
    factory_membership_model(user3.id, org._model.id, member_type='OWNER')
    assert org.get_owner_count() == 2


def test_delete_contact_no_org(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that a contact can not be deleted if it doesn't exist."""
    org = factory_org_service()
    org_dictionary = org.as_dict()
    OrgService.add_contact(org_dictionary['id'], TestContactInfo.contact1)

    OrgService.delete_contact(org_dictionary['id'])

    with pytest.raises(BusinessException) as exception:
        OrgService.delete_contact(org_dictionary['id'])

    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_delete_contact_org_link(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that a contact can not be deleted if it's still being used by an entity."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)

    org = factory_org_service()
    org_dictionary = org.as_dict()
    org_id = org_dictionary['id']

    contact = factory_contact_model()

    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.entity = entity._model  # pylint:disable=protected-access
    contact_link.org = org._model  # pylint:disable=protected-access
    contact_link.commit()

    OrgService.delete_contact(org_id=org_id)
    org = OrgService.find_by_org_id(org_id)
    response = OrgService.get_contacts(org_id)

    assert len(response['contacts']) == 0

    delete_contact_link = ContactLinkModel.find_by_entity_id(entity.identifier)
    assert delete_contact_link

    exist_contact_link = ContactLinkModel.find_by_org_id(org_id)
    assert not exist_contact_link

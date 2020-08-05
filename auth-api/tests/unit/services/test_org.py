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
from flask import current_app

from tests.utilities.factory_scenarios import (
    KeycloakScenario, TestAffidavit, TestBCOLInfo, TestContactInfo, TestEntityInfo, TestJwtClaims, TestOrgInfo,
    TestOrgProductsInfo, TestOrgTypeInfo, TestUserInfo)
from tests.utilities.factory_utils import (
    factory_contact_model, factory_entity_model, factory_entity_service, factory_invitation, factory_membership_model,
    factory_org_model, factory_org_service, factory_user_model, factory_user_model_with_contact)

import auth_api.services.notification as notification
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.services import Affidavit as AffidavitService
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import Invitation as InvitationService
from auth_api.services import Membership as MembershipService
from auth_api.services import Org as OrgService
from auth_api.services import Product as ProductService
from auth_api.services import User as UserService
from auth_api.services.entity import Entity as EntityService
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.constants import GROUP_ACCOUNT_HOLDERS
from auth_api.utils.enums import AccessType, LoginSource, OrgStatus, OrgType, PaymentType, ProductCode


def test_as_dict(session):  # pylint:disable=unused-argument
    """Assert that the Org is exported correctly as a dictinoary."""
    org = factory_org_service()

    dictionary = org.as_dict()
    assert dictionary
    assert dictionary['name'] == TestOrgInfo.org1['name']


def test_create_org(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model()
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org1['name']


def test_create_org_assert_payment_types(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model()
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org1['name']
    payment_settings = dictionary['payment_settings'][0]
    assert payment_settings
    assert payment_settings['preferredPayment'] == PaymentType.CREDIT_CARD.value
    current_app.config['DIRECT_PAY_ENABLED'] = True
    org1 = OrgService.create_org(TestOrgInfo.org2, user_id=user.id)
    assert org1
    dictionary = org1.as_dict()
    assert dictionary['name'] == TestOrgInfo.org2['name']
    payment_settings = dictionary['payment_settings'][0]
    assert payment_settings
    assert payment_settings['preferredPayment'] == PaymentType.DIRECT_PAY.value


def test_create_product_single_subscription(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model()
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org1['name']
    subscriptions = ProductService.create_product_subscription(dictionary['id'], TestOrgProductsInfo.org_products1)
    assert len(subscriptions) == 1
    assert subscriptions[0].product_code == TestOrgProductsInfo.org_products1['subscriptions'][0]['productCode']


def test_create_product_multiple_subscription(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model()
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org1['name']
    subscriptions = ProductService.create_product_subscription(dictionary['id'], TestOrgProductsInfo.org_products2)
    assert len(subscriptions) == 2
    assert subscriptions[0].product_code == TestOrgProductsInfo.org_products2['subscriptions'][0]['productCode']
    assert subscriptions[1].product_code == TestOrgProductsInfo.org_products2['subscriptions'][1]['productCode']


def test_update_org(session):  # pylint:disable=unused-argument
    """Assert that an Org can be updated."""
    org = factory_org_service()

    org.update_org(TestOrgInfo.org2)

    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org2['name']


def test_update_duplicate_org(session):  # pylint:disable=unused-argument
    """Assert that an Org cannot be updated."""
    org = factory_org_service()

    factory_org_model(org_info=TestOrgInfo.org2, org_type_info=TestOrgTypeInfo.implicit, org_status_info=None,
                      payment_type_info=None)

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


def test_get_members(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that members for an org can be retrieved."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    org_dictionary = org.as_dict()

    response = MembershipService.get_members_for_org(org_dictionary['id'],
                                                     status='ACTIVE',
                                                     token_info=TestJwtClaims.public_user_role)
    assert response
    assert len(response) == 1
    assert response[0].membership_type_code == 'ADMIN'


def test_get_invitations(session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that invitations for an org can be retrieved."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        user_with_token = TestUserInfo.user_test
        user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
        user = factory_user_model(user_info=user_with_token)
        org = OrgService.create_org(TestOrgInfo.org1, user.id)
        org_dictionary = org.as_dict()

        invitation_info = factory_invitation(org_dictionary['id'])

        invitation = InvitationService.create_invitation(invitation_info, UserService(user), {}, '')

        response = InvitationService.get_invitations_for_org(org_dictionary['id'], 'PENDING',
                                                             TestJwtClaims.public_user_role)
        assert response
        assert len(response) == 1
        assert response[0].recipient_email == invitation.as_dict()['recipient_email']


def test_get_owner_count_one_owner(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that count of owners is correct."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    assert org.get_owner_count() == 1


def test_get_owner_count_two_owner_with_admins(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that count of owners is correct."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    user2 = factory_user_model(user_info=TestUserInfo.user2)
    factory_membership_model(user2.id, org._model.id, member_type='COORDINATOR')
    user3 = factory_user_model(user_info=TestUserInfo.user3)
    factory_membership_model(user3.id, org._model.id, member_type='ADMIN')
    assert org.get_owner_count() == 2


def test_delete_org_with_members_fail(session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org cannot be deleted."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    user2 = factory_user_model(user_info=TestUserInfo.user2)
    factory_membership_model(user2.id, org._model.id, member_type='COORDINATOR')
    user3 = factory_user_model(user_info=TestUserInfo.user3)
    factory_membership_model(user3.id, org._model.id, member_type='ADMIN')

    with pytest.raises(BusinessException) as exception:
        OrgService.delete_org(org.as_dict()['id'], TestJwtClaims.public_user_role)

    assert exception.value.code == Error.ORG_CANNOT_BE_DISSOLVED.name


def test_delete_org_with_affiliation_fail(session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org cannot be deleted."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    org_id = org.as_dict()['id']

    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']
    AffiliationService.create_affiliation(org_id, business_identifier,
                                          TestEntityInfo.entity_lear_mock['passCode'],
                                          {})

    with pytest.raises(BusinessException) as exception:
        OrgService.delete_org(org_id, TestJwtClaims.public_user_role)

    assert exception.value.code == Error.ORG_CANNOT_BE_DISSOLVED.name

    AffiliationService.delete_affiliation(org_id, business_identifier,
                                          TestEntityInfo.entity_lear_mock['passCode'])
    OrgService.delete_org(org.as_dict()['id'], TestJwtClaims.public_user_role)
    org_inactive = OrgService.find_by_org_id(org.as_dict()['id'])
    assert org_inactive.as_dict()['org_status'] == 'INACTIVE'


def test_delete_org_with_members_success(session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be deleted."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    OrgService.delete_org(org.as_dict()['id'], TestJwtClaims.public_user_role)
    org_inactive = OrgService.find_by_org_id(org.as_dict()['id'])
    assert org_inactive.as_dict()['org_status'] == 'INACTIVE'


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


def test_create_org_adds_user_to_account_holders_group(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org creation adds the user to account holders group."""
    # Create a user in keycloak
    keycloak_service = KeycloakService()
    request = KeycloakScenario.create_user_request()
    keycloak_service.add_user(request, return_if_exists=True)
    kc_user = keycloak_service.get_user_by_username(request.user_name)
    user = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user.id))

    # Patch token info
    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {
            'sub': str(kc_user.id),
            'username': 'public user',
            'realm_access': {
                'roles': [
                ]
            }
        }

    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService._get_token_info', token_info)
    OrgService.create_org(TestOrgInfo.org1, user_id=user.id)

    user_groups = keycloak_service.get_user_groups(user_id=kc_user.id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups


def test_delete_org_removes_user_from_account_holders_group(session, monkeypatch,
                                                            auth_mock):  # pylint:disable=unused-argument
    """Assert that an Org deletion removes the user from account holders group."""
    # Create a user in keycloak
    keycloak_service = KeycloakService()
    request = KeycloakScenario.create_user_request()
    keycloak_service.add_user(request, return_if_exists=True)
    kc_user = keycloak_service.get_user_by_username(request.user_name)
    user = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user.id))

    # Patch token info
    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {
            'sub': str(kc_user.id),
            'username': 'public user',
            'realm_access': {
                'roles': [
                ]
            }
        }

    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService._get_token_info', token_info)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    org = OrgService.delete_org(org.as_dict().get('id'), token_info())

    user_groups = keycloak_service.get_user_groups(user_id=kc_user.id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS not in groups


def test_delete_does_not_remove_user_from_account_holder_group(session, monkeypatch,
                                                               auth_mock):  # pylint:disable=unused-argument
    """Assert that if the user has multiple Orgs, and deleting one doesn't remove account holders group."""
    # Create a user in keycloak
    keycloak_service = KeycloakService()
    request = KeycloakScenario.create_user_request()
    keycloak_service.add_user(request, return_if_exists=True)
    kc_user = keycloak_service.get_user_by_username(request.user_name)
    user = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user.id))

    # Patch token info
    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {
            'sub': str(kc_user.id),
            'username': 'public user',
            'realm_access': {
                'roles': [
                ]
            }
        }

    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService._get_token_info', token_info)
    org1 = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    OrgService.create_org(TestOrgInfo.org2, user_id=user.id)
    OrgService.delete_org(org1.as_dict().get('id'), token_info())

    user_groups = keycloak_service.get_user_groups(user_id=kc_user.id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups


def test_create_org_with_linked_bcol_account(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model()
    org = OrgService.create_org(TestOrgInfo.bcol_linked(), user_id=user.id)
    assert org
    dictionary = org.as_dict()
    payment_settings = dictionary['payment_settings'][0]
    assert payment_settings
    assert payment_settings['preferredPayment'] == PaymentType.BCOL.value
    assert dictionary['name'] == TestOrgInfo.bcol_linked()['name']
    assert dictionary['orgType'] == OrgType.PREMIUM.value


def test_create_org_with_invalid_name_than_bcol_account(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model()

    with pytest.raises(BusinessException) as exception:
        OrgService.create_org(TestOrgInfo.bcol_linked_invalid_name(), user_id=user.id)
    assert exception.value.code == Error.INVALID_INPUT.name


def test_bcol_account_exists(session):  # pylint:disable=unused-argument
    """Assert that the BCOL account is exists."""
    factory_org_service(bcol_info=TestBCOLInfo.bcol1)

    check_result = OrgService.bcol_account_link_check(TestBCOLInfo.bcol1['bcol_account_id'])
    assert check_result


def test_bcol_account_not_exists(session):  # pylint:disable=unused-argument
    """Assert that the BCOL account is not exists."""
    factory_org_service(bcol_info=TestBCOLInfo.bcol1)

    check_result = OrgService.bcol_account_link_check(TestBCOLInfo.bcol2['bcol_account_id'])
    assert not check_result


def test_create_org_with_a_linked_bcol_details(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that org creation with an existing linked BCOL account fails."""
    user = factory_user_model()

    org = OrgService.create_org(TestOrgInfo.bcol_linked(), user_id=user.id)
    assert org
    # Create again

    with pytest.raises(BusinessException) as exception:
        OrgService.create_org(TestOrgInfo.bcol_linked(), user_id=user.id)
    assert exception.value.code == Error.BCOL_ACCOUNT_ALREADY_LINKED.name


def test_create_org_by_bceid_user(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.BCEID.value)

    with patch.object(OrgService, 'send_staff_review_account_reminder', return_value=None) as mock_notify:
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id, token_info=token_info)
        assert org
        dictionary = org.as_dict()
        assert dictionary['name'] == TestOrgInfo.org1['name']
        assert dictionary['org_status'] == OrgStatus.PENDING_AFFIDAVIT_REVIEW.value
        assert dictionary['access_type'] == AccessType.EXTRA_PROVINCIAL.value
        mock_notify.assert_called()


def test_create_org_by_in_province_bceid_user(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.BCEID.value)

    with patch.object(OrgService, 'send_staff_review_account_reminder', return_value=None) as mock_notify:
        org = OrgService.create_org(TestOrgInfo.org_regular_bceid, user_id=user.id, token_info=token_info)
        assert org
        dictionary = org.as_dict()
        assert dictionary['name'] == TestOrgInfo.org1['name']
        assert dictionary['org_status'] == OrgStatus.PENDING_AFFIDAVIT_REVIEW.value
        assert dictionary['access_type'] == AccessType.REGULAR_BCEID.value
        mock_notify.assert_called()


def test_create_org_invalid_access_type_user(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an Org cannot be created by providing wrong access type."""
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.BCEID.value)
    with pytest.raises(BusinessException) as exception:
        OrgService.create_org(TestOrgInfo.org_regular, user_id=user.id, token_info=token_info)
    assert exception.value.code == Error.USER_CANT_CREATE_REGULAR_ORG.name


def test_create_org_by_verified_bceid_user(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    # Steps
    # 1. Create a pending affidavit
    # 2. Create org
    # 3. Approve Org, which will mark the affidavit as approved
    # 4. Same user create new org, which should be ACTIVE.
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.BCEID.value)
    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(token_info=token_info, affidavit_info=affidavit_info)

    with patch.object(OrgService, 'send_staff_review_account_reminder', return_value=None) as mock_notify:
        org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id, token_info=token_info)
        org_dict = org.as_dict()
        assert org_dict['org_status'] == OrgStatus.PENDING_AFFIDAVIT_REVIEW.value
        org = OrgService.approve_or_reject(org_dict['id'], is_approved=True, token_info=token_info)
        org_dict = org.as_dict()
        assert org_dict['org_status'] == OrgStatus.ACTIVE.value

        org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(name='Test 123'), user_id=user.id,
                                    token_info=token_info)
        org_dict = org.as_dict()
        assert org_dict['org_status'] == OrgStatus.ACTIVE.value
        mock_notify.assert_called()


def test_create_org_by_rejected_bceid_user(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    # Steps
    # 1. Create a pending affidavit
    # 2. Create org
    # 3. Reject Org, which will mark the affidavit as rejected
    # 4. Same user create new org, which should be PENDING_AFFIDAVIT_REVIEW.
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.BCEID.value)
    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(token_info=token_info, affidavit_info=affidavit_info)

    with patch.object(OrgService, 'send_staff_review_account_reminder', return_value=None) as mock_notify:
        org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id, token_info=token_info)
        org_dict = org.as_dict()
        assert org_dict['org_status'] == OrgStatus.PENDING_AFFIDAVIT_REVIEW.value
        org = OrgService.approve_or_reject(org_dict['id'], is_approved=False, token_info=token_info)
        org_dict = org.as_dict()
        assert org_dict['org_status'] == OrgStatus.REJECTED.value

        org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(name='Test 123'), user_id=user.id,
                                    token_info=token_info)
        org_dict = org.as_dict()
        assert org_dict['org_status'] == OrgStatus.PENDING_AFFIDAVIT_REVIEW.value
        mock_notify.assert_called()


def test_send_staff_review_account_reminder_exception(session,
                                                      notify_org_mock,
                                                      keycloak_mock):  # pylint:disable=unused-argument
    """Send a reminder with exception."""
    user = factory_user_model_with_contact(TestUserInfo.user_test)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    org_dictionary = org.as_dict()

    with patch.object(notification, 'send_email', return_value=False):
        with pytest.raises(BusinessException) as exception:
            OrgService.send_staff_review_account_reminder(user, org_dictionary['id'], 'localhost')

    assert exception.value.code == Error.FAILED_NOTIFICATION.name


def test_add_product(session):  # pylint:disable=unused-argument
    """Assert that a product can be add into product subscription table."""
    org = factory_org_service()
    org_dictionary = org.as_dict()

    subscriptions = OrgService.add_product(org_dictionary['id'], token_info=None)
    assert subscriptions is None

    subscriptions = OrgService.add_product(org_dictionary['id'], token_info=TestJwtClaims.public_user_role)
    assert len(subscriptions) == 1
    assert subscriptions[0].product_code == ProductCode.BUSINESS.value

    subscriptions = OrgService.add_product(org_dictionary['id'], token_info=TestJwtClaims.system_role)
    assert len(subscriptions) == 1
    assert subscriptions[0].product_code == TestJwtClaims.system_role['product_code']

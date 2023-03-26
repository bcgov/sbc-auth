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
"""Tests for the Product service.

Test suite to ensure that the Product service routines are working as expected.
"""
from unittest.mock import ANY, patch

import pytest

from auth_api.models.contact_link import ContactLink as ContactLinkModel
from auth_api.models.dataclass import Activity
from auth_api.models.membership import Membership
from auth_api.models.product_code import ProductCode as ProductCodeModel
from auth_api.models.product_subscription import ProductSubscription
from auth_api.services.keycloak import KeycloakService
from auth_api.services import Product as ProductService
from auth_api.services import Org
from auth_api.services import User as UserService
from auth_api.services.activity_log_publisher import ActivityLogPublisher

from auth_api.utils.enums import ActivityAction, KeycloakGroupActions, ProductCode, ProductSubscriptionStatus, Status
from tests.utilities.factory_scenarios import KeycloakScenario, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import (
    factory_membership_model, factory_product_model, factory_user_model, patch_token_info)


def test_get_products(session):  # pylint:disable=unused-argument
    """Assert that the product list can be retrieved."""
    response = ProductService.get_products()
    assert response
    # assert the structure is correct by checking for name, description properties in each element
    for item in response:
        assert item['code'] and item['description']


@pytest.mark.parametrize('test_name, has_contact', [
    ('has_contact', True),
    ('no_contact', False),
])
def test_update_product_subscription(session, keycloak_mock, monkeypatch, test_name, has_contact):
    """Assert that updating product subscription works."""
    user = factory_user_model(TestUserInfo.user_test)
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = Org.create_org(TestOrgInfo.org1, user_id=user.id)
    product_subscription = ProductSubscription(org_id=org._model.id,
                                               product_code='PPR',
                                               status_code=ProductSubscriptionStatus.ACTIVE.value
                                               ).flush()

    class MockContact(object):
        email = ''

    class MockPerson(object):
        def __init__(self, contact: MockContact):
            self.contact = contact

    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        if has_contact:
            with patch.object(ContactLinkModel, 'find_by_user_id', return_value=MockPerson(contact=MockContact())):
                ProductService.update_product_subscription(product_subscription.id, True, org._model.id)
        else:
            assert UserService.get_admin_emails_for_org(org.as_dict()['id']) == ''
            ProductService.update_product_subscription(product_subscription.id, True, org._model.id)

        mock_alp.assert_called_with(Activity(action=ActivityAction.ADD_PRODUCT_AND_SERVICE.value,
                                             org_id=ANY, value=ANY, id=ANY, name='Personal Property Registry'))


def test_get_users_product_subscriptions_kc_groups(session, keycloak_mock, monkeypatch):
    """Assert that our keycloak groups are returned correctly."""
    # Used these to test without the keycloak_mock.
    request = KeycloakScenario.create_user_request()
    user = KeycloakService.add_user(request, return_if_exists=True)

    # Set keycloak groups, because empty gets filtered out.
    bca_code = ProductCodeModel.find_by_code('BCA')
    bca_code.keycloak_group = 'bca'
    bca_code.save()
    ppr_code = ProductCodeModel.find_by_code('PPR')
    ppr_code.keycloak_group = 'ppr'
    ppr_code.save()

    vs_code = ProductCodeModel.find_by_code('VS')
    vs_code.keycloak_group = 'vs'
    vs_code.save()

    user1 = factory_user_model(TestUserInfo.get_user_with_kc_guid(user.id))
    patch_token_info({'sub': user.id, 'idp_userid': user1.idp_userid}, monkeypatch)
    org = Org.create_org(TestOrgInfo.org1, user_id=user1.id)
    org_id1 = org.as_dict().get('id')
    factory_membership_model(user1.id, org_id1, member_status=Status.ACTIVE.value)
    factory_product_model(org_id1, product_code=ProductCode.PPR.value,
                          status_code=ProductSubscriptionStatus.ACTIVE.value)

    kc_groups = ProductService.get_users_product_subscriptions_kc_groups([user1.id])
    assert kc_groups[0].user_guid == user1.keycloak_guid
    assert kc_groups[0].group_name == 'bca'
    assert kc_groups[0].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value
    assert kc_groups[1].user_guid == user1.keycloak_guid
    assert kc_groups[1].group_name == 'ppr'
    assert kc_groups[1].group_action == KeycloakGroupActions.ADD_TO_GROUP.value
    assert kc_groups[2].user_guid == user1.keycloak_guid
    assert kc_groups[2].group_name == 'vs'
    assert kc_groups[2].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value

    # Create a user with a membership row that is INACTIVE, subscription ACTIVE.
    user2 = factory_user_model(TestUserInfo.user2)
    factory_membership_model(user2.id, org_id1, member_status=Status.INACTIVE.value)
    factory_membership_model(user2.id, org_id1, member_status=Status.REJECTED.value)
    factory_membership_model(user2.id, org_id1, member_status=Status.PENDING_APPROVAL.value)
    factory_membership_model(user2.id, org_id1, member_status=Status.PENDING_STAFF_REVIEW.value)

    kc_groups = ProductService.get_users_product_subscriptions_kc_groups([user2.id])
    assert kc_groups[0].group_name == 'bca'
    assert kc_groups[0].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value
    assert kc_groups[1].group_name == 'ppr'
    assert kc_groups[1].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value
    assert kc_groups[2].group_name == 'vs'
    assert kc_groups[2].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value

    # Create a user with a membership row that is INACTIVE, ACTIVE
    user3 = factory_user_model(TestUserInfo.user3)
    patch_token_info({'sub': user3.keycloak_guid, 'idp_userid': user3.idp_userid}, monkeypatch)
    factory_membership_model(user3.id, org_id1, member_status=Status.INACTIVE.value)
    factory_membership_model(user3.id, org_id1, member_status=Status.ACTIVE.value)

    kc_groups = ProductService.get_users_product_subscriptions_kc_groups([user3.id])
    assert kc_groups[0].group_name == 'bca'
    assert kc_groups[0].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value
    assert kc_groups[1].group_name == 'ppr'
    assert kc_groups[1].group_action == KeycloakGroupActions.ADD_TO_GROUP.value
    assert kc_groups[2].group_name == 'vs'
    assert kc_groups[2].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value

    # Create a user with a membership row that is ACTIVE, INACTIVE
    user4 = factory_user_model(TestUserInfo.user_staff_admin)
    factory_membership_model(user4.id, org_id1, member_status=Status.ACTIVE.value)
    factory_membership_model(user4.id, org_id1, member_status=Status.INACTIVE.value)

    kc_groups = ProductService.get_users_product_subscriptions_kc_groups([user4.id])
    assert kc_groups[0].group_name == 'bca'
    assert kc_groups[0].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value
    assert kc_groups[1].group_name == 'ppr'
    assert kc_groups[1].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value
    assert kc_groups[2].group_name == 'vs'
    assert kc_groups[2].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value

    # Create a product subscription that is INACTIVE, ACTIVE (should use ACTIVE row, it's latest)
    factory_product_model(org_id1, product_code=ProductCode.BCA.value,
                          status_code=ProductSubscriptionStatus.INACTIVE.value)
    factory_product_model(org_id1, product_code=ProductCode.BCA.value,
                          status_code=ProductSubscriptionStatus.ACTIVE.value)
    factory_membership_model(user4.id, org_id1, member_status=Status.ACTIVE.value)

    kc_groups = ProductService.get_users_product_subscriptions_kc_groups([user4.id])
    assert kc_groups[0].group_name == 'bca'
    assert kc_groups[0].group_action == KeycloakGroupActions.ADD_TO_GROUP.value
    assert kc_groups[1].group_name == 'ppr'
    assert kc_groups[1].group_action == KeycloakGroupActions.ADD_TO_GROUP.value
    assert kc_groups[2].group_name == 'vs'
    assert kc_groups[2].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value

    # Create a product subscription that is ACTIVE, INACTIVE (should use INACTIVE ROW, it's latest)
    factory_product_model(org_id1, product_code=ProductCode.VS.value,
                          status_code=ProductSubscriptionStatus.ACTIVE.value)
    factory_product_model(org_id1, product_code=ProductCode.VS.value,
                          status_code=ProductSubscriptionStatus.INACTIVE.value)

    kc_groups = ProductService.get_users_product_subscriptions_kc_groups([user4.id])
    assert kc_groups[2].user_guid == user4.keycloak_guid
    assert kc_groups[2].group_name == 'vs'
    assert kc_groups[2].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value

    # Create a user with 2 ORG memberships that are opposites
    org = Org.create_org(TestOrgInfo.org2, user_id=user1.id)
    org_id2 = org.as_dict().get('id')
    factory_product_model(org_id2, product_code=ProductCode.PPR.value,
                          status_code=ProductSubscriptionStatus.INACTIVE.value)
    factory_product_model(org_id2, product_code=ProductCode.VS.value,
                          status_code=ProductSubscriptionStatus.ACTIVE.value)
    factory_membership_model(user1.id, org_id2, member_status=Status.ACTIVE.value)

    # BCA and PPR (Org1) and VS (Org2) should be active.
    kc_groups = ProductService.get_users_product_subscriptions_kc_groups([user1.id])
    assert kc_groups[0].group_name == 'bca'
    assert kc_groups[0].group_action == KeycloakGroupActions.ADD_TO_GROUP.value
    assert kc_groups[1].group_name == 'ppr'
    assert kc_groups[1].group_action == KeycloakGroupActions.ADD_TO_GROUP.value
    assert kc_groups[2].group_name == 'vs'
    assert kc_groups[2].group_action == KeycloakGroupActions.ADD_TO_GROUP.value

    # BCA + PPR (Org1) only should be active.
    [membership.delete() for membership in Membership.find_members_by_org_id(org_id2)]
    kc_groups = ProductService.get_users_product_subscriptions_kc_groups([user1.id])
    assert kc_groups[0].group_name == 'bca'
    assert kc_groups[0].group_action == KeycloakGroupActions.ADD_TO_GROUP.value
    assert kc_groups[1].group_name == 'ppr'
    assert kc_groups[1].group_action == KeycloakGroupActions.ADD_TO_GROUP.value
    assert kc_groups[2].group_name == 'vs'
    assert kc_groups[2].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value

    # No product subscriptions should be active.
    [membership.delete() for membership in Membership.find_members_by_org_id(org_id1)]
    kc_groups = ProductService.get_users_product_subscriptions_kc_groups([user1.id])
    assert kc_groups[0].group_name == 'bca'
    assert kc_groups[0].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value
    assert kc_groups[1].group_name == 'ppr'
    assert kc_groups[1].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value
    assert kc_groups[2].group_name == 'vs'
    assert kc_groups[2].group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value

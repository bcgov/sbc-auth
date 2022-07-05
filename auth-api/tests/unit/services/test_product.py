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
from auth_api.models.dataclass import Activity
from auth_api.models.contact_link import ContactLink as ContactLinkModel
from auth_api.models.product_subscription import ProductSubscription
from auth_api.services import Product as ProductService
from auth_api.services import Org
from auth_api.services.activity_log_publisher import ActivityLogPublisher
from auth_api.utils.enums import ActivityAction, ProductSubscriptionStatus
from tests.utilities.factory_scenarios import TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import factory_user_model, patch_token_info


def test_get_products(session):  # pylint:disable=unused-argument
    """Assert that the product list can be retrieved."""
    response = ProductService.get_products()
    assert response
    # assert the structure is correct by checking for name, description properties in each element
    for item in response:
        assert item['code'] and item['description']


def test_update_product_subscription(session, keycloak_mock, monkeypatch):
    """Assert that updating product subscription works."""
    user = factory_user_model(TestUserInfo.user_test)
    patch_token_info({'sub': user.keycloak_guid}, monkeypatch)
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
        with patch.object(ContactLinkModel, 'find_by_user_id', return_value=MockPerson(contact=MockContact())):
            ProductService.update_product_subscription(product_subscription.id, False, org._model.id)
            mock_alp.assert_called_with(Activity(action=ActivityAction.REMOVE_PRODUCT_AND_SERVICE.value,
                                                 org_id=ANY, value=ANY, id=ANY, name='PPR'))
    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        with patch.object(ContactLinkModel, 'find_by_user_id', return_value=MockPerson(contact=MockContact())):
            ProductService.update_product_subscription(product_subscription.id, True, org._model.id)
            mock_alp.assert_called_with(Activity(action=ActivityAction.ADD_PRODUCT_AND_SERVICE.value,
                                        org_id=ANY, value=ANY, id=ANY, name='PPR'))

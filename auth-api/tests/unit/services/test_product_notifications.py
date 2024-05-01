# Copyright © 2023 Province of British Columbia
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
"""Tests for the notifications through the Product service.

Test suite to ensure that the correct product notifications are generated.
"""

from unittest.mock import patch

import mock
import pytest

import auth_api.utils.account_mailer
from auth_api.models import ProductSubscription as ProductSubscriptionModel
from auth_api.models import Task as TaskModel
from auth_api.models.product_code import ProductCode as ProductCodeModel
from auth_api.services import Org as OrgService
from auth_api.services import Product as ProductService
from auth_api.services import Task as TaskService
from auth_api.services.user import User as UserService
from auth_api.utils.enums import (
    LoginSource, QueueMessageTypes, TaskAction, TaskRelationshipStatus, TaskRelationshipType, TaskStatus)
from auth_api.utils.notifications import (
    NotificationAttachmentType, ProductAccessDescriptor, ProductCategoryDescriptor, ProductSubjectDescriptor)
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo, TestOrgProductsInfo, TestUserInfo
from tests.utilities.factory_utils import factory_user_model_with_contact, patch_token_info
from tests.conftest import mock_token


@pytest.mark.parametrize('org_product_info', [
    TestOrgProductsInfo.org_products_vs
])
@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
@patch.object(auth_api.services.products, 'publish_to_mailer')
def test_default_approved_notification(mock_mailer, session, auth_mock, keycloak_mock, monkeypatch, org_product_info):
    """Assert product approved notification default is created."""
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_bceid_user['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_bceid_user['idp_userid']
    user = factory_user_model_with_contact(user_with_token)

    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org_premium, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org_premium['name']

    product_code = org_product_info['subscriptions'][0]['productCode']

    # Subscribe to product
    ProductService.create_product_subscription(org_id=dictionary['id'],
                                               subscription_data=org_product_info,
                                               skip_auth=True)

    org_subscriptions = ProductSubscriptionModel.find_by_org_ids(org_ids=[dictionary['id']])
    org_prod_sub = next(prod for prod in org_subscriptions
                        if prod.product_code == product_code)

    # Fetch products and confirm product subscription is present
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.STAFF.value)
    patch_token_info(token_info, monkeypatch)
    all_subs = ProductService.get_all_product_subscription(org_id=dictionary['id'])

    prod_sub = next(sub for sub in all_subs if sub.get('code') == product_code)

    assert prod_sub
    assert prod_sub['code'] == product_code

    # Staff review task should have been created
    task = TaskModel.find_by_task_relationship_id(
        task_relationship_type=TaskRelationshipType.PRODUCT.value, relationship_id=org_prod_sub.id)

    assert task
    assert task.account_id == dictionary['id']
    assert task.relationship_type == TaskRelationshipType.PRODUCT.value
    assert task.relationship_status == TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
    assert task.relationship_id == org_prod_sub.id
    assert task.action == TaskAction.PRODUCT_REVIEW.value

    # Approve task and check for publish to mailer
    task_info = {
        'relationshipStatus': TaskRelationshipStatus.ACTIVE.value
    }

    product_code_model = ProductCodeModel.find_by_code(product_code)

    with patch.object(UserService, 'get_admin_emails_for_org', return_value='test@test.com'):
        TaskService.update_task(TaskService(task), task_info=task_info)

        expected_data = {
            'productName': product_code_model.description,
            'emailAddresses': 'test@test.com'
        }
        mock_mailer.assert_called_with(QueueMessageTypes.PROD_PACKAGE_APPROVED_NOTIFICATION.value,
                                       data=expected_data)


@pytest.mark.parametrize('org_product_info', [
    TestOrgProductsInfo.org_products_vs
])
@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
@patch.object(auth_api.services.products, 'publish_to_mailer')
def test_default_rejected_notification(mock_mailer, session, auth_mock, keycloak_mock, monkeypatch, org_product_info):
    """Assert product rejected notification default is created."""
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_bceid_user['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_bceid_user['idp_userid']
    user = factory_user_model_with_contact(user_with_token)

    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org_premium, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org_premium['name']

    product_code = org_product_info['subscriptions'][0]['productCode']

    # Subscribe to product
    ProductService.create_product_subscription(org_id=dictionary['id'],
                                               subscription_data=org_product_info,
                                               skip_auth=True)

    org_subscriptions = ProductSubscriptionModel.find_by_org_ids(org_ids=[dictionary['id']])
    org_prod_sub = next(prod for prod in org_subscriptions
                        if prod.product_code == product_code)

    # Fetch products and confirm product subscription is present
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.STAFF.value)
    patch_token_info(token_info, monkeypatch)
    all_subs = ProductService.get_all_product_subscription(org_id=dictionary['id'])

    prod_sub = next(sub for sub in all_subs if sub.get('code') == product_code)

    assert prod_sub
    assert prod_sub['code'] == product_code

    # Staff review task should have been created
    task = TaskModel.find_by_task_relationship_id(
        task_relationship_type=TaskRelationshipType.PRODUCT.value, relationship_id=org_prod_sub.id)

    assert task
    assert task.account_id == dictionary['id']
    assert task.relationship_type == TaskRelationshipType.PRODUCT.value
    assert task.relationship_status == TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
    assert task.relationship_id == org_prod_sub.id
    assert task.action == TaskAction.PRODUCT_REVIEW.value

    # Approve task and check for publish to mailer
    task_info = {
        'relationshipStatus': TaskRelationshipStatus.REJECTED.value
    }

    product_code_model = ProductCodeModel.find_by_code(product_code)

    with patch.object(UserService, 'get_admin_emails_for_org', return_value='test@test.com'):
        TaskService.update_task(TaskService(task), task_info=task_info)

        expected_data = {
            'productName': product_code_model.description,
            'emailAddresses': 'test@test.com'
        }
        mock_mailer.assert_called_with(QueueMessageTypes.PROD_PACKAGE_REJECTED_NOTIFICATION.value,
                                       data=expected_data)


@pytest.mark.parametrize('org_product_info', [
    TestOrgProductsInfo.mhr_qs_lawyer_and_notaries,
    TestOrgProductsInfo.mhr_qs_home_manufacturers,
    TestOrgProductsInfo.mhr_qs_home_dealers
])
@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
@patch.object(auth_api.services.products, 'publish_to_mailer')
def test_detailed_approved_notification(mock_mailer, session, auth_mock, keycloak_mock, monkeypatch, org_product_info):
    """Assert product approved notification with details is created."""
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_bceid_user['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_bceid_user['idp_userid']
    user = factory_user_model_with_contact(user_with_token)

    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org_premium, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org_premium['name']

    product_code = org_product_info['subscriptions'][0]['productCode']
    product_code_model = ProductCodeModel.find_by_code(product_code)

    if product_code_model.parent_code:
        # Create parent product subscription
        ProductService.create_product_subscription(org_id=dictionary['id'],
                                                   subscription_data={'subscriptions': [
                                                       {'productCode': product_code_model.parent_code}]},
                                                   skip_auth=True)

    # Subscribe to product
    ProductService.create_product_subscription(org_id=dictionary['id'],
                                               subscription_data=org_product_info,
                                               skip_auth=True)

    org_subscriptions = ProductSubscriptionModel.find_by_org_ids(org_ids=[dictionary['id']])
    org_prod_sub = next(prod for prod in org_subscriptions
                        if prod.product_code == product_code)

    # Fetch products and confirm product subscription is present
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.STAFF.value)
    patch_token_info(token_info, monkeypatch)
    all_subs = ProductService.get_all_product_subscription(org_id=dictionary['id'])

    prod_sub = next(sub for sub in all_subs if sub.get('code') == product_code)

    assert prod_sub
    assert prod_sub['code'] == product_code

    # Staff review task should have been created
    task = TaskModel.find_by_task_relationship_id(
        task_relationship_type=TaskRelationshipType.PRODUCT.value, relationship_id=org_prod_sub.id)

    assert task
    assert task.account_id == dictionary['id']
    assert task.relationship_type == TaskRelationshipType.PRODUCT.value
    assert task.relationship_status == TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
    assert task.relationship_id == org_prod_sub.id
    assert task.action == TaskAction.QUALIFIED_SUPPLIER_REVIEW.value

    # Approve task and check for publish to mailer
    task_info = {
        'relationshipStatus': TaskRelationshipStatus.ACTIVE.value
    }

    product_code_model = ProductCodeModel.find_by_code(product_code)

    with patch.object(UserService, 'get_admin_emails_for_org', return_value='test@test.com'):
        TaskService.update_task(TaskService(task), task_info=task_info)

        expected_data = {
            'subjectDescriptor': ProductSubjectDescriptor.MHR_QUALIFIED_SUPPLIER.value,
            'productAccessDescriptor': ProductAccessDescriptor.MHR_QUALIFIED_SUPPLIER.value,
            'categoryDescriptor': ProductCategoryDescriptor.MHR.value,
            'isReapproved': False,
            'productName': product_code_model.description,
            'emailAddresses': 'test@test.com'
        }
        mock_mailer.assert_called_with(QueueMessageTypes.PRODUCT_APPROVED_NOTIFICATION_DETAILED.value,
                                       data=expected_data)


@pytest.mark.parametrize('org_product_info, contact_type', [
    (TestOrgProductsInfo.mhr_qs_lawyer_and_notaries, 'BCOL'),
    (TestOrgProductsInfo.mhr_qs_home_manufacturers, 'BCREG'),
    (TestOrgProductsInfo.mhr_qs_home_dealers, 'BCREG')
])
@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
@patch.object(auth_api.services.products, 'publish_to_mailer')
def test_detailed_rejected_notification(mock_mailer, session, auth_mock, keycloak_mock,
                                        monkeypatch, org_product_info, contact_type):
    """Assert product rejected notification with details is created."""
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_bceid_user['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_bceid_user['idp_userid']
    user = factory_user_model_with_contact(user_with_token)

    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org_premium, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org_premium['name']

    product_code = org_product_info['subscriptions'][0]['productCode']
    product_code_model = ProductCodeModel.find_by_code(product_code)

    if product_code_model.parent_code:
        # Create parent product subscription
        ProductService.create_product_subscription(org_id=dictionary['id'],
                                                   subscription_data={'subscriptions': [
                                                       {'productCode': product_code_model.parent_code}]},
                                                   skip_auth=True)

    # Subscribe to product
    ProductService.create_product_subscription(org_id=dictionary['id'],
                                               subscription_data=org_product_info,
                                               skip_auth=True)

    org_subscriptions = ProductSubscriptionModel.find_by_org_ids(org_ids=[dictionary['id']])
    org_prod_sub = next(prod for prod in org_subscriptions
                        if prod.product_code == product_code)

    # Fetch products and confirm product subscription is present
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.STAFF.value)
    patch_token_info(token_info, monkeypatch)
    all_subs = ProductService.get_all_product_subscription(org_id=dictionary['id'])

    prod_sub = next(sub for sub in all_subs if sub.get('code') == product_code)

    assert prod_sub
    assert prod_sub['code'] == product_code

    # Staff review task should have been created
    task = TaskModel.find_by_task_relationship_id(
        task_relationship_type=TaskRelationshipType.PRODUCT.value, relationship_id=org_prod_sub.id)

    assert task
    assert task.account_id == dictionary['id']
    assert task.relationship_type == TaskRelationshipType.PRODUCT.value
    assert task.relationship_status == TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
    assert task.relationship_id == org_prod_sub.id
    assert task.action == TaskAction.QUALIFIED_SUPPLIER_REVIEW.value

    # Approve task and check for publish to mailer
    task_info = {
        'relationshipStatus': TaskRelationshipStatus.REJECTED.value,
        'remarks': ['Test remark']
    }

    product_code_model = ProductCodeModel.find_by_code(product_code)

    with patch.object(UserService, 'get_admin_emails_for_org', return_value='test@test.com'):
        task = TaskService.update_task(TaskService(task), task_info=task_info)
        task_dict = task.as_dict()

        expected_data = {
            'subjectDescriptor': ProductSubjectDescriptor.MHR_QUALIFIED_SUPPLIER.value,
            'productAccessDescriptor': ProductAccessDescriptor.MHR_QUALIFIED_SUPPLIER.value,
            'categoryDescriptor': ProductCategoryDescriptor.MHR.value,
            'accessDisclaimer': True,
            'productName': product_code_model.description,
            'emailAddresses': 'test@test.com',
            'contactType': contact_type,
            'remarks': task_dict['remarks'][0]
        }
        mock_mailer.assert_called_with(QueueMessageTypes.PROD_PACKAGE_REJECTED_NOTIFICATION.value,
                                       data=expected_data)


@pytest.mark.parametrize('org_product_info', [
    TestOrgProductsInfo.mhr_qs_lawyer_and_notaries,
    TestOrgProductsInfo.mhr_qs_home_manufacturers,
    TestOrgProductsInfo.mhr_qs_home_dealers
])
@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
@patch.object(auth_api.services.products, 'publish_to_mailer')
def test_hold_notification(mock_mailer, session, auth_mock, keycloak_mock, monkeypatch, org_product_info):
    """Assert product notification is not created for on hold state."""
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_bceid_user['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_bceid_user['idp_userid']
    user = factory_user_model_with_contact(user_with_token)

    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org_premium, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org_premium['name']

    product_code = org_product_info['subscriptions'][0]['productCode']
    product_code_model = ProductCodeModel.find_by_code(product_code)

    if product_code_model.parent_code:
        # Create parent product subscription
        ProductService.create_product_subscription(org_id=dictionary['id'],
                                                   subscription_data={'subscriptions': [
                                                       {'productCode': product_code_model.parent_code}]},
                                                   skip_auth=True)

    # Subscribe to product
    ProductService.create_product_subscription(org_id=dictionary['id'],
                                               subscription_data=org_product_info,
                                               skip_auth=True)

    org_subscriptions = ProductSubscriptionModel.find_by_org_ids(org_ids=[dictionary['id']])
    org_prod_sub = next(prod for prod in org_subscriptions
                        if prod.product_code == product_code)

    # Fetch products and confirm product subscription is present
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.STAFF.value)
    patch_token_info(token_info, monkeypatch)
    all_subs = ProductService.get_all_product_subscription(org_id=dictionary['id'])

    prod_sub = next(sub for sub in all_subs if sub.get('code') == product_code)

    assert prod_sub
    assert prod_sub['code'] == product_code

    # Staff review task should have been created
    task = TaskModel.find_by_task_relationship_id(
        task_relationship_type=TaskRelationshipType.PRODUCT.value, relationship_id=org_prod_sub.id)

    assert task
    assert task.account_id == dictionary['id']
    assert task.relationship_type == TaskRelationshipType.PRODUCT.value
    assert task.relationship_status == TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
    assert task.relationship_id == org_prod_sub.id
    assert task.action == TaskAction.QUALIFIED_SUPPLIER_REVIEW.value

    # Hold task and check publish to mailer is not called
    task_info = {
        'relationshipStatus': TaskRelationshipStatus.PENDING_STAFF_REVIEW.value,
        'status': TaskStatus.HOLD.value
    }

    with patch.object(UserService, 'get_admin_emails_for_org', return_value='test@test.com'):
        TaskService.update_task(TaskService(task), task_info=task_info)
        mock_mailer.assert_not_called


@pytest.mark.parametrize('org_product_info, contact_type', [
    (TestOrgProductsInfo.mhr_qs_lawyer_and_notaries, 'BCOL'),
    (TestOrgProductsInfo.mhr_qs_home_manufacturers, 'BCREG'),
    (TestOrgProductsInfo.mhr_qs_home_dealers, 'BCREG')
])
@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
@patch.object(auth_api.services.products, 'publish_to_mailer')
def test_confirmation_notification(mock_mailer, session, auth_mock, keycloak_mock,
                                   monkeypatch, org_product_info, contact_type):
    """Assert product confirmation notification is properly created."""
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_bceid_user['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_bceid_user['idp_userid']
    user = factory_user_model_with_contact(user_with_token)

    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org_premium, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org_premium['name']

    product_code = org_product_info['subscriptions'][0]['productCode']
    product_code_model = ProductCodeModel.find_by_code(product_code)

    if product_code_model.parent_code:
        # Create parent product subscription
        ProductService.create_product_subscription(org_id=dictionary['id'],
                                                   subscription_data={'subscriptions': [
                                                       {'productCode': product_code_model.parent_code}]},
                                                   skip_auth=True)

    with patch.object(UserService, 'get_admin_emails_for_org', return_value='test@test.com'):
        # Subscribe to product
        ProductService.create_product_subscription(org_id=dictionary['id'],
                                                   subscription_data=org_product_info,
                                                   skip_auth=True)

        expected_data = {
            'subjectDescriptor': ProductSubjectDescriptor.MHR_QUALIFIED_SUPPLIER.value,
            'productAccessDescriptor': ProductAccessDescriptor.MHR_QUALIFIED_SUPPLIER.value,
            'categoryDescriptor': ProductCategoryDescriptor.MHR.value,
            'productName': product_code_model.description,
            'emailAddresses': 'test@test.com',
            'contactType': contact_type,
            'hasAgreementAttachment': True,
            'attachmentType': NotificationAttachmentType.MHR_QS.value
        }

        mock_mailer.assert_called_with(QueueMessageTypes.PRODUCT_CONFIRMATION_NOTIFICATION.value,
                                       data=expected_data)


@pytest.mark.parametrize('org_product_info', [
    TestOrgProductsInfo.org_products_vs
])
@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
@patch.object(auth_api.services.products, 'publish_to_mailer')
def test_no_confirmation_notification(mock_mailer, session, auth_mock, keycloak_mock, monkeypatch, org_product_info):
    """Assert product confirmation notification not created."""
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_bceid_user['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_bceid_user['idp_userid']
    user = factory_user_model_with_contact(user_with_token)

    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org_premium, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org_premium['name']

    product_code = org_product_info['subscriptions'][0]['productCode']
    product_code_model = ProductCodeModel.find_by_code(product_code)

    if product_code_model.parent_code:
        # Create parent product subscription
        ProductService.create_product_subscription(org_id=dictionary['id'],
                                                   subscription_data={'subscriptions': [
                                                       {'productCode': product_code_model.parent_code}]},
                                                   skip_auth=True)

    with patch.object(UserService, 'get_admin_emails_for_org', return_value='test@test.com'):
        # Subscribe to product
        ProductService.create_product_subscription(org_id=dictionary['id'],
                                                   subscription_data=org_product_info,
                                                   skip_auth=True)
        mock_mailer.assert_not_called()


@pytest.mark.parametrize('org_product_info, contact_type', [
    (TestOrgProductsInfo.mhr_qs_lawyer_and_notaries, 'BCOL'),
    (TestOrgProductsInfo.mhr_qs_home_manufacturers, 'BCREG'),
    (TestOrgProductsInfo.mhr_qs_home_dealers, 'BCREG')
])
@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
@patch.object(auth_api.services.products, 'publish_to_mailer')
def test_resubmission_notification(mock_mailer, session, auth_mock, keycloak_mock,
                                   monkeypatch, org_product_info, contact_type):
    """Assert product resubmission notifications are created."""
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_bceid_user['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_bceid_user['idp_userid']
    user = factory_user_model_with_contact(user_with_token)

    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org_premium, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org_premium['name']

    product_code = org_product_info['subscriptions'][0]['productCode']
    product_code_model = ProductCodeModel.find_by_code(product_code)

    if product_code_model.parent_code:
        # Create parent product subscription
        ProductService.create_product_subscription(org_id=dictionary['id'],
                                                   subscription_data={'subscriptions': [
                                                       {'productCode': product_code_model.parent_code}]},
                                                   skip_auth=True)

    # Subscribe to product
    ProductService.create_product_subscription(org_id=dictionary['id'],
                                               subscription_data=org_product_info,
                                               skip_auth=True)

    org_subscriptions = ProductSubscriptionModel.find_by_org_ids(org_ids=[dictionary['id']])
    org_prod_sub = next(prod for prod in org_subscriptions
                        if prod.product_code == product_code)

    # Fetch products and confirm product subscription is present
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.STAFF.value)
    patch_token_info(token_info, monkeypatch)
    all_subs = ProductService.get_all_product_subscription(org_id=dictionary['id'])

    prod_sub = next(sub for sub in all_subs if sub.get('code') == product_code)

    assert prod_sub
    assert prod_sub['code'] == product_code

    # Staff review task should have been created
    task = TaskModel.find_by_task_relationship_id(
        task_relationship_type=TaskRelationshipType.PRODUCT.value, relationship_id=org_prod_sub.id)

    assert task
    assert task.account_id == dictionary['id']
    assert task.relationship_type == TaskRelationshipType.PRODUCT.value
    assert task.relationship_status == TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
    assert task.relationship_id == org_prod_sub.id
    assert task.action == TaskAction.QUALIFIED_SUPPLIER_REVIEW.value

    # Reject task and check for publish to mailer
    task_info = {
        'relationshipStatus': TaskRelationshipStatus.REJECTED.value,
        'remarks': ['Test remark']
    }
    TaskService.update_task(TaskService(task), task_info=task_info)

    # Resubmit product subscription
    with patch.object(UserService, 'get_admin_emails_for_org', return_value='test@test.com'):
        ProductService.resubmit_product_subscription(org_id=dictionary['id'],
                                                     subscription_data=org_product_info,
                                                     skip_auth=True)

        expected_data = {
            'subjectDescriptor': ProductSubjectDescriptor.MHR_QUALIFIED_SUPPLIER.value,
            'productAccessDescriptor': ProductAccessDescriptor.MHR_QUALIFIED_SUPPLIER.value,
            'categoryDescriptor': ProductCategoryDescriptor.MHR.value,
            'productName': product_code_model.description,
            'emailAddresses': 'test@test.com',
            'contactType': contact_type,
            'hasAgreementAttachment': True,
            'attachmentType': NotificationAttachmentType.MHR_QS.value
        }

        # Assert that confirmation email is re-sent on re-submission
        mock_mailer.assert_called_with(QueueMessageTypes.PRODUCT_CONFIRMATION_NOTIFICATION.value,
                                       data=expected_data)

    # Staff review task should be back in review
    task = TaskModel.find_by_task_relationship_id(
        task_relationship_type=TaskRelationshipType.PRODUCT.value, relationship_id=org_prod_sub.id)

    assert task
    assert task.account_id == dictionary['id']
    assert task.relationship_type == TaskRelationshipType.PRODUCT.value
    assert task.relationship_status == TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
    assert task.relationship_id == org_prod_sub.id
    assert task.action == TaskAction.QUALIFIED_SUPPLIER_REVIEW.value

    # Approve task and check for publish to mailer
    task_info = {
        'relationshipStatus': TaskRelationshipStatus.ACTIVE.value
    }

    product_code_model = ProductCodeModel.find_by_code(product_code)

    # Should use re-approved template
    with patch.object(UserService, 'get_admin_emails_for_org', return_value='test@test.com'):
        TaskService.update_task(TaskService(task), task_info=task_info)

        expected_data = {
            'subjectDescriptor': ProductSubjectDescriptor.MHR_QUALIFIED_SUPPLIER.value,
            'productAccessDescriptor': ProductAccessDescriptor.MHR_QUALIFIED_SUPPLIER.value,
            'categoryDescriptor': ProductCategoryDescriptor.MHR.value,
            'isReapproved': True,
            'productName': product_code_model.description,
            'emailAddresses': 'test@test.com'
        }
        mock_mailer.assert_called_with(QueueMessageTypes.PRODUCT_APPROVED_NOTIFICATION_DETAILED.value,
                                       data=expected_data)

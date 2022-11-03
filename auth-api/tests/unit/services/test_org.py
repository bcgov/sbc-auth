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
from unittest.mock import ANY, Mock, patch

import pytest
from requests import Response
from sqlalchemy import event

from auth_api.models.dataclass import Activity
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Org as OrgModel
from auth_api.models.org import receive_before_insert, receive_before_update
from auth_api.models import Task as TaskModel
from auth_api.services import ActivityLogPublisher
from auth_api.services import Affidavit as AffidavitService
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import Invitation as InvitationService
from auth_api.services import Membership as MembershipService
from auth_api.services import Org as OrgService
from auth_api.services import Product as ProductService
from auth_api.services import Task as TaskService
from auth_api.services import User as UserService
from auth_api.services.entity import Entity as EntityService
from auth_api.services.keycloak import KeycloakService
from auth_api.services.rest_service import RestService
from auth_api.utils.constants import GROUP_ACCOUNT_HOLDERS
from auth_api.utils.enums import (
    AccessType, ActivityAction, LoginSource, OrgStatus, OrgType, PatchActions, PaymentMethod, SuspensionReasonCode,
    TaskAction, TaskRelationshipStatus, TaskStatus)
from tests.utilities.factory_scenarios import (
    KeycloakScenario, TestAffidavit, TestBCOLInfo, TestContactInfo, TestEntityInfo, TestJwtClaims, TestOrgInfo,
    TestOrgProductsInfo, TestOrgTypeInfo, TestPaymentMethodInfo, TestUserInfo)
from tests.utilities.factory_utils import (
    factory_contact_model, factory_entity_model, factory_entity_service, factory_invitation, factory_membership_model,
    factory_org_model, factory_org_service, factory_user_model, factory_user_model_with_contact,
    patch_pay_account_delete, patch_pay_account_post, patch_pay_account_put, patch_token_info)
from tests.utilities.sqlalchemy import clear_event_listeners

# noqa: I005


def test_as_dict(session):  # pylint:disable=unused-argument
    """Assert that the Org is exported correctly as a dictinoary."""
    org = factory_org_service()

    dictionary = org.as_dict()
    assert dictionary
    assert dictionary['name'] == TestOrgInfo.org1['name']


def test_create_org(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model()
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org1['name']


def test_create_org_products(session, keycloak_mock, monkeypatch):
    """Assert that an Org with products can be created."""
    user = factory_user_model()
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        org = OrgService.create_org(TestOrgInfo.org_with_products, user_id=user.id)
        mock_alp.assert_called_with(Activity(action=ActivityAction.ADD_PRODUCT_AND_SERVICE.value,
                                             org_id=ANY, value=ANY, id=ANY, name='Business Registry & Name Request'))
        assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org_with_products['name']


def test_create_basic_org_assert_pay_request_is_correct(session, keycloak_mock,
                                                        monkeypatch):  # pylint:disable=unused-argument
    """Assert that while org creation , pay-api gets called with proper data for basic accounts."""
    user = factory_user_model()
    with patch.object(RestService, 'post') as mock_post:
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
        assert org
        dictionary = org.as_dict()
        assert dictionary['name'] == TestOrgInfo.org1['name']
        mock_post.assert_called()
        actual_data = mock_post.call_args.kwargs.get('data')
        expected_data = {
            'accountId': dictionary.get('id'),
            'accountName': dictionary.get('name'),
            'paymentInfo': {
                'methodOfPayment': OrgService._get_default_payment_method_for_creditcard()
            }

        }
        assert expected_data == actual_data


def test_pay_request_is_correct_with_branch_name(session,
                                                 keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that while org creation , pay-api gets called with proper data for basic accounts."""
    user = factory_user_model()
    with patch.object(RestService, 'post') as mock_post:
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org_branch_name, user_id=user.id)
        assert org
        dictionary = org.as_dict()
        assert dictionary['name'] == TestOrgInfo.org_branch_name['name']
        mock_post.assert_called()
        actual_data = mock_post.call_args.kwargs.get('data')
        expected_data = {
            'accountId': dictionary.get('id'),
            'accountName': f"{dictionary.get('name')}-{TestOrgInfo.org_branch_name['branchName']}",
            'paymentInfo': {
                'methodOfPayment': OrgService._get_default_payment_method_for_creditcard()
            }

        }
        assert expected_data == actual_data


def test_update_basic_org_assert_pay_request_activity(session, keycloak_mock, monkeypatch):
    """Assert that while org payment update touches activity log."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    # Have to patch this because the pay spec is wrong and returns 201, not 202 or 200.
    patch_pay_account_post(monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    new_payment_method = TestPaymentMethodInfo.get_payment_method_input(PaymentMethod.ONLINE_BANKING)

    patch_token_info(TestJwtClaims.public_user_role, monkeypatch)

    # Have to patch this because the pay spec is wrong and returns 201, not 202 or 200.
    patch_pay_account_put(monkeypatch)
    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        org = OrgService.update_org(org, new_payment_method)
        mock_alp.assert_called_with(Activity(action=ActivityAction.PAYMENT_INFO_CHANGE.value,
                                             org_id=ANY, name=ANY, id=ANY,
                                             value=PaymentMethod.ONLINE_BANKING.value))


def test_update_basic_org_assert_pay_request_is_correct(session, keycloak_mock,
                                                        monkeypatch):  # pylint:disable=unused-argument
    """Assert that while org updation , pay-api gets called with proper data for basic accounts."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    with patch.object(RestService, 'put') as mock_put:
        new_payment_method = TestPaymentMethodInfo.get_payment_method_input(PaymentMethod.ONLINE_BANKING)
        patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
        org = OrgService.update_org(org, new_payment_method)
        assert org
        dictionary = org.as_dict()
        mock_put.assert_called()
        actual_data = mock_put.call_args.kwargs.get('data')
        expected_data = {
            'accountId': dictionary.get('id'),
            'accountName': dictionary.get('name'),
            'paymentInfo': {
                'methodOfPayment': PaymentMethod.ONLINE_BANKING.value
            }

        }
        assert expected_data == actual_data, 'updating to Online Banking works.'

        new_payment_method = TestPaymentMethodInfo.get_payment_method_input(PaymentMethod.DIRECT_PAY)
        patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
        org = OrgService.update_org(org, new_payment_method)
        assert org
        dictionary = org.as_dict()
        mock_put.assert_called()
        actual_data = mock_put.call_args.kwargs.get('data')
        expected_data = {
            'accountId': dictionary.get('id'),
            'accountName': dictionary.get('name'),
            'paymentInfo': {
                'methodOfPayment': PaymentMethod.DIRECT_PAY.value
            }

        }
        assert expected_data == actual_data, 'updating bank  to Credit Card works.'


def test_create_basic_org_assert_pay_request_is_correct_online_banking(session,
                                                                       keycloak_mock,
                                                                       monkeypatch):  # pylint:disable=unused-argument
    """Assert that while org creation , pay-api gets called with proper data for basic accounts."""
    user = factory_user_model()
    with patch.object(RestService, 'post') as mock_post:
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org_onlinebanking, user_id=user.id)
        assert org
        dictionary = org.as_dict()
        assert dictionary['name'] == TestOrgInfo.org1['name']
        mock_post.assert_called()
        actual_data = mock_post.call_args.kwargs.get('data')
        expected_data = {
            'accountId': dictionary.get('id'),
            'accountName': dictionary.get('name'),
            'paymentInfo': {
                'methodOfPayment': PaymentMethod.ONLINE_BANKING.value
            }

        }
        assert expected_data == actual_data


def test_create_basic_org_assert_pay_request_is_govm(session,
                                                     keycloak_mock, staff_user_mock,
                                                     monkeypatch):  # pylint:disable=unused-argument
    """Assert that while org creation , pay-api gets called with proper data for basic accounts."""
    user = factory_user_model()
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.STAFF.value,
                                             roles=['create_accounts'])
    with patch.object(RestService, 'post') as mock_post:
        patch_token_info(token_info, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org_govm, user_id=user.id)
        assert org
        dictionary = org.as_dict()
        assert dictionary['name'] == TestOrgInfo.org_govm['name']
        mock_post.assert_called()
        actual_data = mock_post.call_args.kwargs.get('data')
        expected_data = {
            'accountId': dictionary.get('id'),
            'accountName': dictionary.get('name') + '-' + dictionary.get('branch_name'),
            'paymentInfo': {
                'methodOfPayment': PaymentMethod.EJV.value
            }

        }
        assert expected_data == actual_data


def test_put_basic_org_assert_pay_request_is_govm(session,
                                                  keycloak_mock, staff_user_mock,
                                                  monkeypatch):  # pylint:disable=unused-argument
    """Assert that while org creation , pay-api gets called with proper data for basic accounts."""
    user = factory_user_model()
    staff_token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.STAFF.value,
                                                   roles=['create_accounts'], idp_userid=user.idp_userid)
    user2 = factory_user_model(TestUserInfo.user2)
    public_token_info = TestJwtClaims.get_test_user(sub=user2.keycloak_guid, source=LoginSource.STAFF.value,
                                                    roles=['gov_account_user'], idp_userid=user2.idp_userid)
    patch_token_info(staff_token_info, monkeypatch)
    org: OrgService = OrgService.create_org(TestOrgInfo.org_govm, user_id=user.id)
    assert org
    with patch.object(RestService, 'put') as mock_post:
        payment_details = TestPaymentMethodInfo.get_payment_method_input_with_revenue()
        org_body = {
            'mailingAddress': TestOrgInfo.get_mailing_address(),
            **payment_details

        }
        patch_token_info(public_token_info, monkeypatch)
        with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
            org = OrgService.update_org(org, org_body)
            mock_alp.assert_called_with(Activity(action=ActivityAction.ACCOUNT_ADDRESS_CHANGE.value,
                                        org_id=ANY, name=ANY, id=ANY,
                                        value=ANY))
            assert org
        dictionary = org.as_dict()
        assert dictionary['name'] == TestOrgInfo.org_govm['name']
        mock_post.assert_called()
        actual_data = mock_post.call_args.kwargs.get('data')
        expected_data = {
            'accountId': dictionary.get('id'),
            'accountName': dictionary.get('name') + '-' + dictionary.get('branch_name'),
            'paymentInfo': {
                'methodOfPayment': 'EJV',
                'revenueAccount': payment_details.get('paymentInfo').get('revenueAccount')
            },
            'contactInfo': TestOrgInfo.get_mailing_address()

        }
        assert expected_data == actual_data


def test_create_premium_org_assert_pay_request_is_correct(session, keycloak_mock,
                                                          monkeypatch):  # pylint:disable=unused-argument
    """Assert that while org creation , pay-api gets called with proper data for basic accounts."""
    bcol_response = Mock(spec=Response)
    bcol_response.json.return_value = {'userId': 'PB25020', 'accountNumber': '180670',
                                       'orgName': 'BC ONLINE TECHNICAL TEAM DEVL'}
    bcol_response.status_code = 200

    pay_api_response = Mock(spec=Response)
    pay_api_response.status_code = 201

    with patch.object(RestService, 'post', side_effect=[bcol_response, pay_api_response]) as mock_post:
        user = factory_user_model()
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.bcol_linked(), user_id=user.id)
        assert org
        dictionary = org.as_dict()
        mock_post.assert_called()
        actual_data = mock_post.call_args_list[1].kwargs.get('data')
        expected_data = {
            'accountId': dictionary.get('id'),
            'accountName': TestOrgInfo.bcol_linked().get('name'),
            'paymentInfo': {
                'methodOfPayment': PaymentMethod.BCOL.value
            },
            'bcolAccountNumber': dictionary.get('bcol_account_id'),
            'bcolUserId': dictionary.get('bcol_user_id'),
            'contactInfo': TestOrgInfo.bcol_linked().get('mailingAddress')

        }
        assert actual_data == expected_data


def test_create_org_assert_payment_types(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model()
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org1['name']
    assert dictionary.get('bcol_user_id', None) is None
    assert dictionary.get('bcol_user_name', None) is None
    assert dictionary.get('bcol_account_id', None) is None


def test_create_product_single_subscription(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_bceid_user['sub']
    user = factory_user_model(user_with_token)
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org1['name']
    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)
    subscriptions = ProductService.create_product_subscription(dictionary['id'],
                                                               TestOrgProductsInfo.org_products1,
                                                               skip_auth=True)
    assert next(prod for prod in subscriptions
                if prod.get('code') == TestOrgProductsInfo.org_products1['subscriptions'][0]['productCode'])


def test_create_product_single_subscription_duplicate_error(session, keycloak_mock,
                                                            monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_bceid_user['sub']
    user = factory_user_model(user_with_token)
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org1['name']

    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)
    subscriptions = ProductService.create_product_subscription(dictionary['id'],
                                                               TestOrgProductsInfo.org_products_business,
                                                               skip_auth=True)
    assert next(prod for prod in subscriptions
                if prod.get('code') == TestOrgProductsInfo.org_products_business['subscriptions'][0]['productCode'])

    with pytest.raises(BusinessException) as exception:
        ProductService.create_product_subscription(dictionary['id'],
                                                   TestOrgProductsInfo.org_products_business,
                                                   skip_auth=True)
    assert exception.value.code == Error.PRODUCT_SUBSCRIPTION_EXISTS.name


def test_create_product_multiple_subscription(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_bceid_user['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_bceid_user['idp_userid']
    user = factory_user_model(user_with_token)
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TestOrgInfo.org1['name']

    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)
    subscriptions = ProductService.create_product_subscription(dictionary['id'],
                                                               TestOrgProductsInfo.org_products2,
                                                               skip_auth=True)
    assert next(prod for prod in subscriptions
                if prod.get('code') == TestOrgProductsInfo.org_products2['subscriptions'][0]['productCode'])
    assert next(prod for prod in subscriptions
                if prod.get('code') == TestOrgProductsInfo.org_products2['subscriptions'][1]['productCode'])


@pytest.mark.parametrize(
    'org_type', [(OrgType.STAFF.value), (OrgType.SBC_STAFF.value)]
)
def test_create_product_subscription_staff(session, keycloak_mock, org_type, monkeypatch):
    """Assert that updating product subscription works for staff."""
    user = factory_user_model(TestUserInfo.user_test)
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)

    # Clearing the event listeners here, because we can't change the type_code.
    clear_event_listeners(OrgModel)
    org_db = OrgModel.find_by_id(org._model.id)
    org_db.type_code = org_type
    org_db.save()
    event.listen(OrgModel, 'before_update', receive_before_update, raw=True)
    event.listen(OrgModel, 'before_insert', receive_before_insert)

    subscriptions = ProductService.create_product_subscription(org._model.id,
                                                               TestOrgProductsInfo.org_products2,
                                                               skip_auth=True)

    assert next(prod for prod in subscriptions
                if prod.get('code') == TestOrgProductsInfo.org_products2['subscriptions'][0]['productCode'])
    assert next(prod for prod in subscriptions
                if prod.get('code') == TestOrgProductsInfo.org_products2['subscriptions'][1]['productCode'])


def test_create_org_with_duplicate_name(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org with duplicate name cannot be created."""
    user = factory_user_model()
    org = factory_org_service()

    factory_org_model(org_info=TestOrgInfo.org2, org_type_info=TestOrgTypeInfo.implicit)

    with pytest.raises(BusinessException) as exception:
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        org.create_org(TestOrgInfo.org2, user_id=user.id)
    assert exception.value.code == Error.DATA_CONFLICT.name


def test_create_org_with_similar_name(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org with similar name can be created."""
    user = factory_user_model()
    org = factory_org_service()

    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    new_org = org.create_org({'name': 'My Test'}, user_id=user.id)
    dictionary = new_org.as_dict()

    assert dictionary['name'] == 'My Test'


def test_create_org_with_duplicate_name_bcol(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org linking to bcol retrun exception if there's duplicated names."""
    org = factory_org_service()

    factory_org_model({'name': 'BC ONLINE TECHNICAL TEAM DEVL'}, org_type_info=TestOrgTypeInfo.implicit)
    bcol_response = Mock(spec=Response)
    bcol_response.json.return_value = {'userId': 'PB25020', 'accountNumber': '180670',
                                       'orgName': 'BC ONLINE TECHNICAL TEAM DEVL'}
    bcol_response.status_code = 200

    pay_api_response = Mock(spec=Response)
    pay_api_response.status_code = 201

    with patch.object(RestService, 'post', side_effect=[bcol_response, pay_api_response]):
        user = factory_user_model()
        with pytest.raises(BusinessException) as exception:
            patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
            org.create_org(TestOrgInfo.bcol_linked(), user_id=user.id)
        assert exception.value.code == Error.DATA_CONFLICT.name


def test_update_org_name(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org name cannot be updated."""
    org = factory_org_service()

    with patch.object(RestService, 'put') as mock_put:
        with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
            org = org.update_org({'name': 'My Test'})
            mock_alp.assert_called_with(Activity(action=ActivityAction.ACCOUNT_NAME_CHANGE.value,
                                                 org_id=ANY, value='My Test', id=ANY,
                                                 name=ANY))
        assert org
        dictionary = org.as_dict()
        mock_put.assert_called()
        actual_data = mock_put.call_args.kwargs.get('data')
        expected_data = {
            'accountId': dictionary.get('id'),
            'accountName': dictionary.get('name'),
        }
        assert expected_data == actual_data, 'name update work.'


def test_update_org(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be updated."""
    org = factory_org_service()
    org.update_org(TestOrgInfo.update_org_with_business_type)

    dictionary = org.as_dict()
    assert dictionary['business_type'] == TestOrgInfo.update_org_with_business_type['businessType']


def test_suspend_org(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be updated."""
    org = factory_org_service()
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid)

    patch_token_info(token_info, monkeypatch)
    updated_org = org.change_org_status(OrgStatus.SUSPENDED.value,
                                        SuspensionReasonCode.OWNER_CHANGE.name)
    assert updated_org.as_dict()['status_code'] == OrgStatus.SUSPENDED.value
    assert updated_org.as_dict()['suspension_reason_code'] == SuspensionReasonCode.OWNER_CHANGE.name

    updated_org = org.change_org_status(OrgStatus.ACTIVE.value,
                                        SuspensionReasonCode.DISPUTE.name)
    assert updated_org.as_dict()['status_code'] == OrgStatus.ACTIVE.value


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


def test_find_org_by_name(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an org can be retrieved by its name."""
    org = factory_org_service()
    dictionary = org.as_dict()
    org_name = dictionary['name']

    found_org = OrgService.find_by_org_name(org_name)

    assert found_org
    assert found_org.get('orgs')[0].get('name') == org_name


def test_find_org_by_name_branch_name(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an org can be retrieved by its name annd branch nanme."""
    org = factory_org_service(org_info=TestOrgInfo.org2)
    dictionary = org.as_dict()
    org_name = dictionary['name']
    branch_name = dictionary['branch_name']

    found_org = OrgService.find_by_org_name(org_name)

    assert found_org
    assert found_org.get('orgs')[0].get('name') == org_name

    found_org = OrgService.find_by_org_name(org_name, branch_name=branch_name)

    assert found_org
    assert found_org.get('orgs')[0].get('name') == org_name
    assert found_org.get('orgs')[0].get('branch_name') == branch_name


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


def test_get_members(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that members for an org can be retrieved."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_user_role['idp_userid']
    user = factory_user_model(user_info=user_with_token)
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    org_dictionary = org.as_dict()

    patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
    response = MembershipService.get_members_for_org(org_dictionary['id'],
                                                     status='ACTIVE')
    assert response
    assert len(response) == 1
    assert response[0].membership_type_code == 'ADMIN'


def test_get_invitations(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that invitations for an org can be retrieved."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        user_with_token = TestUserInfo.user_test
        user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
        user_with_token['idp_userid'] = TestJwtClaims.public_user_role['idp_userid']
        user = factory_user_model(user_info=user_with_token)

        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org1, user.id)
        org_dictionary = org.as_dict()

        invitation_info = factory_invitation(org_dictionary['id'])

        invitation = InvitationService.create_invitation(invitation_info, UserService(user), '')

        patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
        response = InvitationService.get_invitations_for_org(org_dictionary['id'], 'PENDING')
        assert response
        assert len(response) == 1
        assert response[0].recipient_email == invitation.as_dict()['recipient_email']


def test_get_owner_count_one_owner(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that count of owners is correct."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    assert org.get_owner_count() == 1


@pytest.mark.parametrize(
    'staff_org', [(TestOrgInfo.staff_org), (TestOrgInfo.sbc_staff_org)]
)
def test_create_staff_org_failure(session, keycloak_mock, staff_org, monkeypatch):  # pylint:disable=unused-argument
    """Assert that staff org cannot be created."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    with pytest.raises(BusinessException) as exception:
        OrgService.create_org(TestOrgInfo.staff_org, user.id)
    assert exception.value.code == Error.INVALID_INPUT.name


def test_get_owner_count_two_owner_with_admins(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert wrong org cannot be created."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)

    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    user2 = factory_user_model(user_info=TestUserInfo.user2)
    factory_membership_model(user2.id, org._model.id, member_type='COORDINATOR')
    user3 = factory_user_model(user_info=TestUserInfo.user3)
    factory_membership_model(user3.id, org._model.id, member_type='ADMIN')
    assert org.get_owner_count() == 2


def test_delete_org_with_members(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an org can be deleted."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_user_role['idp_userid']
    user = factory_user_model(user_info=user_with_token)

    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    user2 = factory_user_model(user_info=TestUserInfo.user2)
    factory_membership_model(user2.id, org._model.id, member_type='COORDINATOR')
    user3 = factory_user_model(user_info=TestUserInfo.user3)
    factory_membership_model(user3.id, org._model.id, member_type='ADMIN')

    patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
    patch_pay_account_delete(monkeypatch)
    org_id = org.as_dict()['id']

    OrgService.delete_org(org_id)
    assert len(MembershipService.get_members_for_org(org_id)) == 0


def test_delete_org_with_affiliation(session, auth_mock, keycloak_mock,
                                     monkeypatch):  # pylint:disable=unused-argument
    """Assert that an org cannot be deleted."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user = factory_user_model(user_info=user_with_token)

    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)
    org_id = org.as_dict()['id']

    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']
    AffiliationService.create_affiliation(org_id, business_identifier,
                                          TestEntityInfo.entity_lear_mock['passCode'])

    patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
    patch_pay_account_delete(monkeypatch)
    OrgService.delete_org(org_id)

    assert len(AffiliationService.find_visible_affiliations_by_org_id(org_id)) == 0


def test_delete_org_with_members_success(session, auth_mock, keycloak_mock,
                                         monkeypatch):  # pylint:disable=unused-argument
    """Assert that an org can be deleted."""
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_user_role['idp_userid']
    user = factory_user_model(user_info=user_with_token)

    patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user.id)

    patch_pay_account_delete(monkeypatch)
    OrgService.delete_org(org.as_dict()['id'])
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
    OrgService.find_by_org_id(org_id)
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

    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    OrgService.create_org(TestOrgInfo.org1, user_id=user.id)

    user_groups = keycloak_service.get_user_groups(user_id=kc_user.id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups


def test_delete_org_removes_user_from_account_holders_group(session, auth_mock,
                                                            monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org deletion removes the user from account holders group."""
    # Create a user in keycloak
    keycloak_service = KeycloakService()
    request = KeycloakScenario.create_user_request()
    keycloak_service.add_user(request, return_if_exists=True)
    kc_user = keycloak_service.get_user_by_username(request.user_name)
    user = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user.id))

    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    patch_pay_account_delete(monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    OrgService.delete_org(org.as_dict().get('id'))

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

    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    patch_pay_account_delete(monkeypatch)
    org1 = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    OrgService.create_org(TestOrgInfo.org2, user_id=user.id)
    OrgService.delete_org(org1.as_dict().get('id'))

    user_groups = keycloak_service.get_user_groups(user_id=kc_user.id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups


def test_create_org_with_linked_bcol_account(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model()
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.bcol_linked(), user_id=user.id)
    assert org
    dictionary = org.as_dict()

    assert dictionary['name'] == TestOrgInfo.bcol_linked()['name']
    assert dictionary['org_type'] == OrgType.PREMIUM.value
    assert dictionary['bcol_user_id'] is not None
    assert dictionary['bcol_account_id'] is not None
    assert dictionary['bcol_account_name'] is not None


def test_bcol_account_exists(session):  # pylint:disable=unused-argument
    """Assert that the BCOL account is exists."""
    factory_org_service(bcol_info=TestBCOLInfo.bcol1)

    check_result = OrgService.bcol_account_link_check(TestBCOLInfo.bcol1['bcol_account_id'])
    assert check_result


def test_create_org_with_different_name_than_bcol_account(session, keycloak_mock,
                                                          monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model()

    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.bcol_linked_different_name(), user_id=user.id)
    assert org
    dictionary = org.as_dict()

    assert dictionary['name'] == TestOrgInfo.bcol_linked_different_name()['name']
    assert dictionary['org_type'] == OrgType.PREMIUM.value
    assert dictionary['bcol_user_id'] is not None
    assert dictionary['bcol_account_id'] is not None
    assert dictionary['bcol_account_name'] is not None


def test_bcol_account_not_exists(session):  # pylint:disable=unused-argument
    """Assert that the BCOL account is not exists."""
    factory_org_service(bcol_info=TestBCOLInfo.bcol1)

    check_result = OrgService.bcol_account_link_check(TestBCOLInfo.bcol2['bcol_account_id'])
    assert not check_result


def test_create_org_with_a_linked_bcol_details(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that org creation with an existing linked BCOL account fails."""
    user = factory_user_model()
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.bcol_linked(), user_id=user.id)
    assert org
    # Create again

    with pytest.raises(BusinessException) as exception:
        OrgService.create_org(TestOrgInfo.bcol_linked(), user_id=user.id)
    assert exception.value.code == Error.BCOL_ACCOUNT_ALREADY_LINKED.name


def test_create_org_by_bceid_user(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid)
    patch_token_info(token_info, monkeypatch)

    with patch.object(OrgService, 'send_staff_review_account_reminder', return_value=None) as mock_notify:
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
        assert org
        dictionary = org.as_dict()
        assert dictionary['name'] == TestOrgInfo.org1['name']
        assert dictionary['org_status'] == OrgStatus.PENDING_STAFF_REVIEW.value
        assert dictionary['access_type'] == AccessType.EXTRA_PROVINCIAL.value
        mock_notify.assert_called()


def test_create_org_by_in_province_bceid_user(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid)
    monkeypatch.setattr('auth_api.utils.user_context._get_token_info', lambda: token_info)

    with patch.object(OrgService, 'send_staff_review_account_reminder', return_value=None) as mock_notify:
        org = OrgService.create_org(TestOrgInfo.org_regular_bceid, user_id=user.id)
        assert org
        dictionary = org.as_dict()
        assert dictionary['name'] == TestOrgInfo.org1['name']
        assert dictionary['org_status'] == OrgStatus.PENDING_STAFF_REVIEW.value
        assert dictionary['access_type'] == AccessType.REGULAR_BCEID.value
        mock_notify.assert_called()


def test_create_org_invalid_access_type_user(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org cannot be created by providing wrong access type."""
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid)
    monkeypatch.setattr('auth_api.utils.user_context._get_token_info', lambda: token_info)
    with pytest.raises(BusinessException) as exception:
        OrgService.create_org(TestOrgInfo.org_regular, user_id=user.id)
    assert exception.value.code == Error.USER_CANT_CREATE_REGULAR_ORG.name


def test_create_org_by_verified_bceid_user(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    # Steps
    # 1. Create a pending affidavit
    # 2. Create org
    # 3. Approve Org, which will mark the affidavit as approved
    # 4. Same user create new org, which should be ACTIVE.
    user = factory_user_model_with_contact(user_info=TestUserInfo.user_bceid_tester)
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid)
    patch_token_info(token_info, monkeypatch)

    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(affidavit_info=affidavit_info)
    org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id)
    org_dict = org.as_dict()
    assert org_dict['org_status'] == OrgStatus.PENDING_STAFF_REVIEW.value

    task_model = TaskModel.find_by_task_for_account(org_dict['id'], status=TaskStatus.OPEN.value)
    assert task_model.relationship_id == org_dict['id']
    assert task_model.action == TaskAction.AFFIDAVIT_REVIEW.value

    task_info = {
        'status': TaskStatus.OPEN.value,
        'relationshipStatus': TaskRelationshipStatus.ACTIVE.value,
    }
    TaskService.update_task(TaskService(task_model), task_info)
    org_result: OrgModel = OrgModel.find_by_org_id(org_dict['id'])
    assert org_result.status_code == OrgStatus.ACTIVE.value


def test_create_org_by_rejected_bceid_user(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    # Steps
    # 1. Create a pending affidavit
    # 2. Create org
    # 3. Reject Org, which will mark the affidavit as rejected
    # 4. Same user create new org, which should be PENDING_STAFF_REVIEW.
    user = factory_user_model_with_contact(user_info=TestUserInfo.user_bceid_tester)
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid)

    patch_token_info(token_info, monkeypatch)
    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(affidavit_info=affidavit_info)

    with patch.object(OrgService, 'send_staff_review_account_reminder', return_value=None) as mock_notify:
        org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id)
        org_dict = org.as_dict()
        assert org_dict['org_status'] == OrgStatus.PENDING_STAFF_REVIEW.value
        org_dict = org.as_dict()
        assert org_dict['org_status'] == OrgStatus.PENDING_STAFF_REVIEW.value

        task_model = TaskModel.find_by_task_for_account(org_dict['id'], status=TaskStatus.OPEN.value)
        assert task_model.relationship_id == org_dict['id']
        assert task_model.action == TaskAction.AFFIDAVIT_REVIEW.value

        task_info = {
            'status': TaskStatus.OPEN.value,
            'relationshipStatus': TaskRelationshipStatus.REJECTED.value,
        }
        TaskService.update_task(TaskService(task_model), task_info)
        org_result: OrgModel = OrgModel.find_by_org_id(org_dict['id'])
        assert org_result.status_code == OrgStatus.REJECTED.value

        org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(name='Test 123'), user_id=user.id)
        org_dict = org.as_dict()
        assert org_dict['org_status'] == OrgStatus.PENDING_STAFF_REVIEW.value
        mock_notify.assert_called()


def test_change_org_access_type(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org can be updated."""
    org = factory_org_service()
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.BCEID.value)

    patch_token_info(token_info, monkeypatch)
    updated_org = org.change_org_access_type(AccessType.GOVN.value)
    assert updated_org.as_dict()['access_type'] == AccessType.GOVN.value


def test_patch_org_status(session, monkeypatch, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Org status can be updated."""
    org = factory_org_service()
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid)
    patch_token_info(token_info, monkeypatch)

    # Validate and update org status
    patch_info = {
        'action': PatchActions.UPDATE_STATUS.value,
        'statusCode': OrgStatus.SUSPENDED.value,
    }
    with pytest.raises(BusinessException) as exception:
        org.patch_org(PatchActions.UPDATE_STATUS.value, patch_info)
    assert exception.value.code == Error.INVALID_INPUT.name

    patch_info['suspensionReasonCode'] = SuspensionReasonCode.OWNER_CHANGE.name
    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        updated_org = org.patch_org(PatchActions.UPDATE_STATUS.value, patch_info)
        mock_alp.assert_called_with(Activity(action=ActivityAction.ACCOUNT_SUSPENSION.value,
                                             org_id=ANY, name=ANY, id=ANY,
                                             value=SuspensionReasonCode.OWNER_CHANGE.value))
        assert updated_org['status_code'] == OrgStatus.SUSPENDED.value

    patch_info = {
        'action': PatchActions.UPDATE_STATUS.value,
        'statusCode': OrgStatus.ACTIVE.value,
    }
    updated_org = org.patch_org(PatchActions.UPDATE_STATUS.value, patch_info)
    assert updated_org['status_code'] == OrgStatus.ACTIVE.value

    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        OrgService.update_login_option(org._model.id, 'BCROS')
        mock_alp.assert_called_with(Activity(action=ActivityAction.AUTHENTICATION_METHOD_CHANGE.value,
                                             org_id=ANY, name=ANY, id=ANY, value='BCROS'))


def test_patch_org_access_type(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Org access type can be updated."""
    org = factory_org_service()
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(sub=user.keycloak_guid, source=LoginSource.BCEID.value)
    patch_token_info(token_info, monkeypatch)

    # Validate and update org status
    patch_info = {
        'action': PatchActions.UPDATE_ACCESS_TYPE.value
    }
    with pytest.raises(BusinessException) as exception:
        org.patch_org(PatchActions.UPDATE_ACCESS_TYPE.value, patch_info)
    assert exception.value.code == Error.INVALID_INPUT.name

    patch_info['accessType'] = AccessType.GOVM.value
    with pytest.raises(BusinessException) as exception:
        org.patch_org(PatchActions.UPDATE_ACCESS_TYPE.value, patch_info)
    assert exception.value.code == Error.INVALID_INPUT.name

    patch_info['accessType'] = AccessType.GOVN.value
    updated_org = org.patch_org(PatchActions.UPDATE_ACCESS_TYPE.value, patch_info)
    assert updated_org['access_type'] == AccessType.GOVN.value

import datetime
import json
import random

import pytest
import requests
from pylenium import Pylenium

from tests.pages.paybc import PayBCPage
from tests.utilities.settings import get_path_settings, get_settings, get_test_data


class TestPayment:
    """Payment test suite."""

    # Only excute these tests by main flow.
    __test__ = False

    def test_get_fees(self, testing_config, logger):
        """Test get fee."""
        load_data = get_test_data(testing_config.test_data['fee_schedule'])
        call_url = f'{testing_config.pay_api_url}/fees/{load_data["corp_type_code"]}/{load_data["filing_type_code"]}'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_create_creditcard_payment(self, testing_config, logger):
        """Test creating creaditcard payment."""
        load_data = get_test_data(testing_config.test_data['creditcard'])
        testing_config.payment_method = load_data['methodOfPayment']
        input_data = json.dumps({
            "paymentInfo": {
                "methodOfPayment": testing_config.payment_method
            },
            "businessInfo": {
                "businessIdentifier": testing_config.business_identifier,
                "corpType": "CP",
                "businessName": "ABC Corp",
                "contactInfo": {
                    "city": "Victoria",
                    "postalCode": "V8P2P2",
                    "province": "BC",
                    "addressLine1": "100 Douglas Street",
                    "country": "CA"
                }
            },
            "filingInfo": {
                "filingTypes": [
                    {
                        "filingTypeCode": "OTANN"
                    }
                ]
            }
        })
        call_url = f'{testing_config.pay_api_url}/payment-requests'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.payment_id = response_json.get('id')
        testing_config.invoice_id = response_json.get('invoices')[0].get('id')
        testing_config.payment_method = load_data['methodOfPayment']

    def test_get_payment(self, testing_config, logger):
        """Test get payment."""
        call_url = f'{testing_config.pay_api_url}/payment-requests/{testing_config.payment_id}'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_get_invoices(self, testing_config, logger):
        """Test get invovices."""
        call_url = f'{testing_config.pay_api_url}/payment-requests/{testing_config.payment_id}/invoices'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_get_invoice(self, testing_config, logger):
        """Test get invovices."""
        call_url = f'{testing_config.pay_api_url}/payment-requests/{testing_config.payment_id}/invoices/{testing_config.invoice_id}'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_update_payment(self, testing_config, logger):
        input_data = json.dumps({
            "paymentInfo": {
                "methodOfPayment": testing_config.payment_method
            },
            "businessInfo": {
                "businessIdentifier": testing_config.business_identifier,
                "corpType": "CP",
                "businessName": "ABC Corp",
                "contactInfo": {
                    "city": "Victoria",
                    "postalCode": "V8P2P2",
                    "province": "BC",
                    "addressLine1": "100 Douglas Street",
                    "country": "CA"
                }
            },
            "filingInfo": {
                "filingTypes": [
                    {
                        "filingTypeCode": "OTANN"
                    }
                ]
            }
        })
        call_url = f'{testing_config.pay_api_url}/payment-requests/{testing_config.payment_id}'
        logger.debug(f'[ACTION] Put {call_url} with {input_data}')
        response = requests.put(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                         'Content-Type': 'application/json'},
                                data=input_data)
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_create_transaction(self, testing_config, logger):
        input_data = json.dumps({
            "clientSystemUrl": f"{get_settings().ROOT_URL}/{testing_config.business_identifier}/?filing_id=85448",
            "payReturnUrl": f"{get_path_settings().PAYMENT_RETURN}"
        })
        call_url = f'{testing_config.pay_api_url}/payment-requests/{testing_config.payment_id}/transactions'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.transaction_id = response_json.get('id')
        testing_config.pay_system_url = response_json.get('paySystemUrl')

    def test_get_transactions(self, testing_config, logger):
        call_url = f'{testing_config.pay_api_url}/payment-requests/{testing_config.payment_id}/transactions'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()

    def test_get_paybc_status(self, testing_config, logger):
        call_url = f'{testing_config.status_api_url}/status/PAYBC'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url)
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.paybc_status = response_json.get('currentStatus')

        if testing_config.paybc_status:
            response = requests.head(testing_config.pay_system_url)
            if response.status_code != 200:
                testing_config.paybc_status = 'False'

    @pytest.mark.skip_paybc_status('False')
    def test_pay_by_paybc(self, testing_config, test_case, py_config, selenium, request):
        """Access login pages to get the session storage values."""
        py = Pylenium(py_config, test_case.logger)
        paybc_page = PayBCPage(py)
        paybc_page.run(url=testing_config.pay_system_url, creditcard=get_settings().PAYBC_CREDITCARD,
                       cvv=get_settings().PAYBC_CREDITCARD_CVV)

    @pytest.mark.skip_paybc_status('False')
    def test_update_transaction(self, testing_config, logger):
        input_data = json.dumps({})
        call_url = f'{testing_config.pay_api_url}/payment-requests/{testing_config.payment_id}/transactions/{testing_config.transaction_id}'
        logger.debug(f'[ACTION] Patch {call_url} with {input_data}')
        response = requests.patch(call_url,
                                  headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                           'Content-Type': 'application/json'},
                                  data=input_data)
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_get_transaction(self, testing_config, logger):
        call_url = f'{testing_config.pay_api_url}/payment-requests/{testing_config.payment_id}/transactions/{testing_config.transaction_id}'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.payment_status = response_json.get('statusCode')

    @pytest.mark.skip_payment_status('COMPLETED')
    def test_generate_receipt_with_payment_id(self, testing_config, logger):
        input_data = json.dumps({
            "corpName": testing_config.business_identifier,
            "filingDateTime": "June 27, 2019",
            "fileName": "director-change"
        })
        call_url = f'{testing_config.pay_api_url}/payment-requests/{testing_config.payment_id}/receipts'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.debug(f'[ACTION] Response: {response.status_code}')

    @pytest.mark.skip_payment_status('COMPLETED')
    def test_generate_receipt_with_payment_and_invoice_id(self, testing_config, logger):
        input_data = json.dumps({
            "corpName": testing_config.business_identifier,
            "filingDateTime": "June 27, 2019",
            "fileName": "director-change"
        })
        call_url = f'{testing_config.pay_api_url}/payment-requests/{testing_config.payment_id}/invoices/{testing_config.invoice_id}/receipts'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.debug(f'[ACTION] Response: {response.status_code}')

    @pytest.mark.skip_org_type('BASIC')
    def test_get_transactions(self, testing_config, logger):
        """Test get payment transactions."""
        input_data = json.dumps({'dateFilter': {'startDate': '01/01/2020',
                                                'endDate': '12/31/2020'}, 'folioNumber': ''})
        call_url = f'{testing_config.pay_api_url}/accounts/{testing_config.org_id}/payments/queries?page=1&limit=10'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_delete_completed_payment(self, testing_config, logger):
        """Test delete the payment with 'COMPLETED"""
        call_url = f'{testing_config.pay_api_url}/payment-requests/{testing_config.payment_id}'
        logger.debug(f'[ACTION] Delete {call_url}')
        response = requests.delete(call_url,
                                   headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        if testing_config.payment_status == 'COMPLETED':
            assert response.status_code == 400
        else:
            assert response.status_code == 202
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

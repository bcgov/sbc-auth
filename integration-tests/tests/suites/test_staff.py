import datetime
import json
import requests
import pytest
import urllib.request

from tests.utilities.settings import get_test_data, setup_access_data


@pytest.mark.incremental
@pytest.mark.parametrize('login_session', setup_access_data('STAFF', ['STAFF']), indirect=True, scope='class')
@pytest.mark.usefixtures('setup_data')
class TestStaff:

    __test__ = True

    def test_business_details(self, testing_config, logger):
        """Test get business details from legal api."""
        input_data = get_test_data(testing_config.test_data['business'])
        call_url = f'{testing_config.legal_api_url}/businesses/{input_data["businessIdentifier"]}'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_get_accounts_by_staff(self, testing_config, logger):
        """Test get accounts by staff."""
        call_url = f'{testing_config.auth_api_url}/users/orgs?status=PENDING_AFFIDAVIT_REVIEW'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

        call_url = f'{testing_config.auth_api_url}/orgs?status=ACTIVE&page=1&limit=10'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

        call_url = f'{testing_config.auth_api_url}/orgs?status=REJECTED'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

        call_url = f'{testing_config.auth_api_url}/orgs?status=PENDING_ACTIVATION'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_get_product_code(self, testing_config, logger):
        """Test get produce codes."""
        call_url = f'{testing_config.auth_api_url}/codes/product_code'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_get_org_type(self, testing_config, logger):
        """Test get produce codes."""
        call_url = f'{testing_config.auth_api_url}/codes/org_type'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_create_account(self, testing_config, logger):
        """Test create account."""
        input_data = json.dumps(get_test_data(testing_config.test_data['org']))
        call_url = f'{testing_config.auth_api_url}/orgs'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.org_id = response_json.get('id')

    def test_create_products(self, testing_config, logger):
        """Test create products."""
        input_data = json.dumps({"subscriptions": [{"productCode": "DIR_SEARCH", "productRoles": ["search"]},
                                                   {"productCode": "VS", "productRoles": ["search"]},
                                                   {"productCode": "BCA", "productRoles": ["search"]},
                                                   {"productCode": "BUSINESS", "productRoles": ["search"]},
                                                   {"productCode": "PPR", "productRoles": ["search"]}]})
        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/products'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_create_invitations(self, testing_config, logger):
        """Test create invitation."""
        load_data = get_test_data(testing_config.test_data['invitation'])
        input_data = json.dumps({
            'recipientEmail': load_data['recipientEmail'],
            'sentDate': datetime.datetime.now().strftime('Y-%m-%d %H:%M:%S'),
            'membership': [
                {
                    'membershipType': 'ADMIN',
                    'orgId': testing_config.org_id
                }
            ]
        })
        call_url = f'{testing_config.auth_api_url}/invitations'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.notification_id = response_json.get('id')
        testing_config.invitation_json = response_json

    def test_get_invitations(self, testing_config, logger):
        """Test get pending invitations."""
        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/invitations?status=PENDING'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_resend_invitations(self, testing_config, logger):
        """Test resend invitation."""
        input_data = json.dumps(testing_config.invitation_json)
        call_url = f'{testing_config.auth_api_url}/invitations/{testing_config.notification_id}'
        logger.debug(f'[ACTION] Patch {call_url} with {input_data}')
        response = requests.patch(call_url,
                                  headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                           'Content-Type': 'application/json'},
                                  data=input_data)
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

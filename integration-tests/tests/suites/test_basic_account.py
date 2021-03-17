import datetime
import json
import random

import pytest
import requests

from tests.suites.test_payment import TestPayment
from tests.utilities.settings import get_settings, get_test_data, setup_access_data


@pytest.mark.incremental
@pytest.mark.parametrize('login_session', setup_access_data('BASIC', ['BCSC']), indirect=True, scope='class')
@pytest.mark.usefixtures('setup_data')
class TestBasicAccount(TestPayment):
    """Basic account test suite."""

    __test__ = True

    def test_get_user_profile(self, testing_config, logger):
        """Test get user profile. After login, the user should be created in db."""
        call_url = f'{testing_config.auth_api_url}/users/@me'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(f'{call_url}',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.user_id = response_json.get('keycloakGuid')

    def test_get_last_terms(self, testing_config, logger):
        """Get last version of termofuse."""
        call_url = f'{testing_config.auth_api_url}/documents/termsofuse'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.terms_version = response_json.get('versionId')

    def test_accept_terms(self, testing_config, logger):
        """Test accept termofuser."""
        input_data = json.dumps({'termsversion': testing_config.terms_version, 'istermsaccepted': True})
        call_url = f'{testing_config.auth_api_url}/users/@me'
        logger.debug(f'[ACTION] Patch {call_url} with {input_data}')
        response = requests.patch(call_url,
                                  headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                           'Content-Type': 'application/json'},
                                  data=input_data)
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_get_user_profile(self, testing_config, logger):
        """Test get user profile."""
        call_url = f'{testing_config.auth_api_url}/users/@me'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(f'{testing_config.auth_api_url}/users/@me',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.user_id = response_json.get('keycloakGuid')

    @pytest.mark.skip_login_as('COORDINATOR')
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

    def test_create_user_profile(self, testing_config, logger):
        """Test create user profile (contact information)."""
        input_data = json.dumps(get_test_data(testing_config.test_data['user_profile']))
        call_url = f'{testing_config.auth_api_url}/users/contacts'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    @pytest.mark.skip_login_as('ADMIN')
    def test_accept_invitation(self, tested_user, testing_config, logger):
        """Test member user accecpt inviation."""
        for config in tested_user.config:
            token = config.invitation_token
            call_url = f'{testing_config.auth_api_url}/invitations/tokens/{token}'
            logger.debug(f'[ACTION] Put {call_url}')
            response = requests.put(call_url,
                                    headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
            assert response.status_code == 200
            logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
            break

    @pytest.mark.skip_login_as('ADMIN')
    def test_admin_approve_invitation(self, tested_user, testing_config, logger):
        """Test admin user approve invitation."""
        input_data = json.dumps(get_test_data(testing_config.test_data['member']))
        for config in tested_user.config:
            token = config.keycloak_token
            testing_config.org_id = config.org_id
            call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/members?status=PENDING_APPROVAL'
            logger.debug(f'[ACTION] Get {call_url} with {input_data}')
            response = requests.get(call_url,
                                    headers={'Authorization': f'Bearer {token}'})
            assert response.status_code == 200
            logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
            response_json = response.json()
            testing_config.member_id = response_json.get('members')[0]['id']
            call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/members/{testing_config.member_id}'
            logger.debug(f'[ACTION] Patch {call_url} with {input_data}')
            response = requests.patch(call_url,
                                      headers={'Authorization': f'Bearer {token}',
                                               'Content-Type': 'application/json'},
                                      data=input_data)
            assert response.status_code == 200
            logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
            break

    def test_get_account(self, testing_config, logger):
        """Test get account."""
        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.org_type = response_json.get('orgType')

    def test_get_user_settings(self, testing_config, logger):
        """Test get user settings."""
        call_url = f'{testing_config.auth_api_url}/users/{testing_config.user_id}/settings'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    @pytest.mark.skip_login_as('COORDINATOR')
    def test_create_invitations(self, testing_config, logger):
        """Test create invitation."""
        load_data = get_test_data(testing_config.test_data['invitation'])
        input_data = json.dumps({
            'recipientEmail': load_data['recipientEmail'],
            'sentDate': datetime.datetime.now().strftime('Y-%m-%d %H:%M:%S'),
            'membership': [
                {
                    'membershipType': load_data['membershipType'],
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
        testing_config.invitation_token = response_json.get('token')

    @pytest.mark.skip_login_as('COORDINATOR')
    def test_get_invitations(self, testing_config, logger):
        """Test get pending invitations."""
        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/invitations?status=PENDING'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_get_membership(self, testing_config, logger):
        """Test get membership."""
        call_url = f'{testing_config.auth_api_url}/users/orgs/{testing_config.org_id}/membership'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/members?status=ACTIVE'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/members?status=PENDING_APPROVAL'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    @pytest.mark.skip_login_as('COORDINATOR')
    def test_get_notification_status(self, testing_config, logger):
        """Test get notification status."""
        # Request URL: https://notify-api-dev.pathfinder.gov.bc.ca/api/v1/notification/
        # Request Method: GET
        pass

    @pytest.mark.skip_login_as('COORDINATOR')
    def test_create_affiliation(self, testing_config, logger):
        """Test create affiliation."""
        input_data = json.dumps(get_test_data(testing_config.test_data['business']))
        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/affiliations'
        logger.debug(f'[ACTION] Get {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_get_affiliations(self, testing_config, logger):
        """Test get affiliated businesses."""
        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/affiliations'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.business_identifier = response_json.get('entities')[0].get('businessIdentifier')

    def test_business_details(self, testing_config, logger):
        """Test get business details from legal api."""
        call_url = f'{testing_config.legal_api_url}/businesses/{testing_config.business_identifier}'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

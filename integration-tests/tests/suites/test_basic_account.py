import datetime
import json
import random

import pytest
import requests

from tests.suites.test_payment import TestPayment
from tests.utilities.settings import get_settings, get_test_data, setup_access_data


@pytest.mark.incremental
@pytest.mark.parametrize('login_session', setup_access_data('BASIC', ['BCSC', 'BCEID']), indirect=True, scope='class')
@pytest.mark.usefixtures('setup_data')
class TestBasicAccount(TestPayment):
    """Basic account test suite."""

    __test__ = True

    def test_get_user_profile(self, testing_config, logger):
        """Test get user profile. After login, the user should be created in db."""
        call_url = f'{testing_config.auth_api_url}/users/@me'
        logger.action(f'Get {call_url}', is_subaction=True)
        response = requests.get(f'{call_url}',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)
        response_json = response.json()
        testing_config.user_id = response_json.get('keycloakGuid')

    def test_get_last_terms(self, testing_config, logger):
        """Get last version of termofuse."""
        call_url = f'{testing_config.auth_api_url}/documents/termsofuse'
        logger.action(f'Get {call_url}', is_subaction=True)
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)
        response_json = response.json()
        testing_config.terms_version = response_json.get('version_id')

    def test_accept_terms(self, testing_config, logger):
        """Test accept termofuser."""
        input_data = json.dumps({'termsversion': testing_config.terms_version, 'istermsaccepted': True})
        call_url = f'{testing_config.auth_api_url}/users/@me'
        logger.action(f'Patch {call_url} with {input_data}', is_subaction=True)
        response = requests.patch(call_url,
                                  headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                           'Content-Type': 'application/json'},
                                  data=input_data)
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)

    def test_get_user_profile(self, testing_config, logger):
        """Test get user profile."""
        call_url = f'{testing_config.auth_api_url}/users/@me'
        logger.action(f'Get {call_url}', is_subaction=True)
        response = requests.get(f'{testing_config.auth_api_url}/users/@me',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)
        response_json = response.json()
        testing_config.user_id = response_json.get('keycloakGuid')

    @pytest.mark.skip_login_as('COORDINATOR')
    def test_create_account(self, testing_config, logger):
        """Test create account."""
        input_data = json.dumps(get_test_data(testing_config.test_data['org']))
        call_url = f'{testing_config.auth_api_url}/orgs'
        logger.action(f'Post {call_url} with {input_data}', is_subaction=True)
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)
        response_json = response.json()
        testing_config.org_id = response_json.get('id')
        testing_config.org_type = response_json.get('orgType')

    def test_create_user_profile(self, testing_config, logger):
        """Test create user profile (contact information)."""
        input_data = json.dumps(get_test_data(testing_config.test_data['user_profile']))
        call_url = f'{testing_config.auth_api_url}/users/contacts'
        logger.action(f'Post {call_url} with {input_data}', is_subaction=True)
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)

    @pytest.mark.skip_login_as('ADMIN')
    def test_accept_invitation(self, tested_user, testing_config, logger):
        """Test member user accecpt inviation."""
        for config in tested_user.config:
            token = config.invitation_token
            call_url = f'{testing_config.auth_api_url}/invitations/tokens/{token}'
            logger.action(f'Put {call_url}', is_subaction=True)
            response = requests.put(call_url,
                                    headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
            assert response.status_code == 200
            logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)
            break

    @pytest.mark.skip_login_as('ADMIN')
    def test_admin_approve_invitation(self, tested_user, testing_config, logger):
        """Test admin user approve invitation."""
        input_data = json.dumps(get_test_data(testing_config.test_data['member']))
        for config in tested_user.config:
            token = config.keycloak_token
            testing_config.org_id = config.org_id
            call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/members?status=PENDING_APPROVAL'
            logger.action(f'Get {call_url} with {input_data}', is_subaction=True)
            response = requests.get(call_url,
                                    headers={'Authorization': f'Bearer {token}'})
            assert response.status_code == 200
            logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)
            response_json = response.json()
            testing_config.member_id = response_json.get('members')[0]['id']
            call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/members/{testing_config.member_id}'
            logger.action(f'Patch {call_url} with {input_data}', is_subaction=True)
            response = requests.patch(call_url,
                                      headers={'Authorization': f'Bearer {token}',
                                               'Content-Type': 'application/json'},
                                      data=input_data)
            assert response.status_code == 200
            logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)
            break

    def test_get_account(self, testing_config, logger):
        """Test get account."""
        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}'
        logger.action(f'Get {call_url}', is_subaction=True)
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)

    def test_get_user_settings(self, testing_config, logger):
        """Test get user settings."""
        call_url = f'{testing_config.auth_api_url}/users/{testing_config.user_id}/settings'
        logger.action(f'Get {call_url}', is_subaction=True)
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)

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
        logger.action(f'Post {call_url} with {input_data}', is_subaction=True)
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)
        response_json = response.json()
        testing_config.notification_id = response_json.get('id')
        testing_config.invitation_token = response_json.get('token')

    @pytest.mark.skip_login_as('COORDINATOR')
    def test_get_invitations(self, testing_config, logger):
        """Test get pending invitations."""
        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/invitations?status=PENDING'
        logger.action(f'Get {call_url}', is_subaction=True)
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)

    def test_get_membership(self, testing_config, logger):
        """Test get membership."""
        call_url = f'{testing_config.auth_api_url}/users/orgs/{testing_config.org_id}/membership'
        logger.action(f'Get {call_url}', is_subaction=True)
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)

        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/members?status=ACTIVE'
        logger.action(f'Get {call_url}', is_subaction=True)
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)

        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/members?status=PENDING_APPROVAL'
        logger.action(f'Get {call_url}', is_subaction=True)
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)

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
        logger.action(f'Get {call_url} with {input_data}', is_subaction=True)
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)

    def test_get_affiliations(self, testing_config, logger):
        """Test get affiliated businesses."""
        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/affiliations'
        logger.action(f'Get {call_url}', is_subaction=True)
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)
        response_json = response.json()
        testing_config.business_identifier = response_json.get('entities')[0].get('businessIdentifier')

    def test_business_details(self, testing_config, logger):
        """Test get business details from legal api."""
        call_url = f'{testing_config.legal_api_url}/businesses/{testing_config.business_identifier}'
        logger.action(f'Get {call_url}', is_subaction=True)
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.action(f'Response: {response.status_code} {response.json()}', is_subaction=True)

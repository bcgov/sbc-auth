import datetime
import json
import requests
import pytest
import random

from tests.suites.test_payment import TestPayment
from tests.utilities.settings import get_settings, get_test_data, setup_access_data


@pytest.mark.incremental
@pytest.mark.parametrize('login_session', setup_access_data('PREMIUM', ['BCSC']), indirect=True, scope='class')
@pytest.mark.usefixtures('setup_data')
class TestPremiumAccount:

    __test__ = True

    def test_get_user_profile(self, testing_config, logger):
        """Test get user profile. After login, the user should be created in db."""
        response = requests.get(f'{testing_config.auth_api_url}/users/@me',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        response_json = response.json()
        testing_config.user_id = response_json.get('keycloakGuid')

    def test_get_last_terms(self, testing_config, logger):
        """Get last version of termofuse."""
        response = requests.get(f'{testing_config.auth_api_url}/documents/termsofuse',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        response_json = response.json()
        testing_config.terms_version = response_json.get('versionId')

    def test_accept_terms(self, testing_config, logger):
        """Test accept termofuser."""
        input_data = json.dumps({'termsversion': testing_config.terms_version, 'istermsaccepted': True})
        response = requests.patch(f'{testing_config.auth_api_url}/users/@me',
                                  headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                           'Content-Type': 'application/json'},
                                  data=input_data)
        assert response.status_code == 200

    def test_get_user_profile(self, testing_config, logger):
        """Test get user profile."""
        response = requests.get(f'{testing_config.auth_api_url}/users/@me',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        response_json = response.json()
        testing_config.user_id = response_json.get('keycloakGuid')

    @pytest.mark.skip_login_as('bcsc_member')
    def test_link_bcol_account(self, testing_config, logger):
        """Test link bcol account."""
        load_data = random.sample(get_settings().BCOL_USERS, 1)[0]
        input_data = json.dumps({
            'userId': load_data.username,
            'password': load_data.password
        })
        response = requests.post(f'{testing_config.auth_api_url}/bcol-profiles',
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 200
        response_json = response.json()

    @pytest.mark.skip_login_as('bcsc_member')
    def test_create_account(self, testing_config, logger):
        """Test create account."""
        input_data = json.dumps(get_test_data(testing_config.test_data['org']))
        response = requests.post(f'{testing_config.auth_api_url}/orgs',
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)

        assert response.status_code == 201
        response_json = response.json()
        testing_config.org_id = response_json.get('id')

    def test_create_user_profile(self, testing_config, logger):
        """Test create user profile (contact information)."""
        input_data = json.dumps(get_test_data(testing_config.test_data['user_profile']))
        response = requests.post(f'{testing_config.auth_api_url}/users/contacts',
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201

    def test_get_account(self, testing_config, logger):
        """Test get account."""
        response = requests.get(f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200

    def test_get_user_settings(self, testing_config, logger):
        """Test get user settings."""
        response = requests.get(f'{testing_config.auth_api_url}/users/{testing_config.user_id}/settings',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200

    def test_get_user_notifications(self, testing_config, logger):
        """Test get user notifications."""
        response = requests.get(f'{testing_config.auth_api_url}/users/{testing_config.user_id}/org/{testing_config.org_id}/notifications',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200

import datetime
import json
import requests
import pytest
import random

from tests.suites.test_payment import TestPayment
from tests.utilities.settings import get_settings, get_test_data, setup_access_data


@pytest.mark.incremental
@pytest.mark.parametrize('login_session', setup_access_data('BASIC', ['BCSC']), indirect=True, scope='class')
@pytest.mark.usefixtures('setup_data')
class TestAnonymouse:

    __test__ = True

    def test_get_user_profile(self, testing_config, logger):
        """Test get user profile. After login, the user should be created in db."""
        response = requests.get(f'{testing_config.auth_api_url}/users/@me',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        response_json = response.json()
        testing_config.user_id = response_json.get('keycloakGuid')

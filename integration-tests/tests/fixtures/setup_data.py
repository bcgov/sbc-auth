import json
import pytest
import requests
from pylenium import Pylenium

from tests.pages.bcsc_invitation_login import BCSCInvitationLoginPage
from tests.pages.bcsc_login import BCSCLoginPage
from tests.utilities.session_storage import SessionStorage
from tests.utilities.settings import get_settings, load_data_from_csv
from tests.utilities.testing_config import TestedUser, TestingConfig


@pytest.fixture(scope='module')
def tested_user(request) -> TestedUser:
    """Test suite configuration to store all of user and related information during testing."""
    print('\n\nSetting up testing config\n')

    user = TestedUser()

    def teardown():
        """After testing done, reset all the test data."""
        print('\n\nTeardown\n')
        for config in user.config:
            # Walk through test users's token and call reset endpoint to reset data.
            response = requests.post(f'{config.reset_api_url}',
                                     headers={'Authorization': f'Bearer {config.keycloak_token}'})
            assert response.status_code == 204

    request.addfinalizer(teardown)

    return user


@pytest.fixture(scope='class')
def login_session(test_case, py_config, selenium, tested_user, request) -> SessionStorage:
    """Access login pages to get the session storage values."""
    py = Pylenium(py_config, test_case.logger)
    params = request.param
    if params['loginAs'] in ['ADMIN']:
        login_page = BCSCLoginPage(py)
        login_page.run(url=f'{params["path"]}',
                       username=params['username'],
                       password=params['password'])
    elif params['loginAs'] in ['COORDINATOR']:
        for config in tested_user.config:
            invitation_token = config.invitation_token
            if invitation_token:
                login_page = BCSCInvitationLoginPage(py)
                login_page.run(url=f'{params["path"]}/{invitation_token}',
                               username=params['username'],
                               password=params['password'])
                break

    login_session = SessionStorage(py)
    login_session.login_as = params['loginAs']
    login_session.username = params['username']
    yield login_session
    py.quit()

    return login_session


@pytest.fixture(scope='class')
def testing_config(login_session) -> TestingConfig:
    """Get Login configuration from session storage."""
    testing_config = TestingConfig()
    testing_config.login_as = login_session.login_as
    testing_config.keycloak_token = login_session.get('KEYCLOAK_TOKEN')
    testing_config.username = login_session.username

    auth_api_config: dict = json.loads(login_session.get('AUTH_API_CONFIG'))
    testing_config.auth_api_url = auth_api_config['VUE_APP_AUTH_ROOT_API']
    testing_config.pay_api_url = auth_api_config['VUE_APP_PAY_ROOT_API']
    testing_config.bcol_api_url = auth_api_config['VUE_APP_BCOL_ROOT_API']
    testing_config.legal_api_url = auth_api_config['VUE_APP_LEGAL_ROOT_API']
    testing_config.reset_api_url = auth_api_config['VUE_APP_AUTH_RESET_API']
    testing_config.status_api_url = auth_api_config['VUE_APP_STATUS_ROOT_API']

    return testing_config


@pytest.fixture(autouse=True)
def log_test_name(logger, request):
    """Log the test name when test it."""
    test_name = request.node.name
    logger.step(f'{test_name}')


@pytest.yield_fixture(scope='class')
def setup_data(testing_config, tested_user, logger):
    """Prepare from csv and Save test data for each user test suite."""
    # setup test data
    testing_config.test_data = load_data_from_csv()
    logger.debug(f'testing_config: {testing_config}')
    yield
    tested_user.config.append(testing_config)

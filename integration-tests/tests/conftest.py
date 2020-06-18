"""
`conftest.py` and `pylenium.json` files should stay at your Workspace Root.

conftest.py
    Although this file is editable, you should only change its contents if you know what you are doing.
    Instead, you can create your own conftest.py file in the folder where you store your tests.

pylenium.json
    You can change the values, but DO NOT touch the keys or you will break the schema.

py
    The only fixture you really need from this is `py`. This is the instance of Pylenium for each test.
    Just pass py into your test and you're ready to go!

Examples:
    def test_go_to_google(py):
        py.visit('https://google.com')
        assert 'Google' in py.title
"""

import json
import os
import shutil
import time
from typing import Dict, Tuple

import pytest
import requests
from faker import Faker
from pylenium import Pylenium
from pylenium.config import PyleniumConfig, TestCase
from pylenium.logging import Logger

from tests.pages.bcsc_invitation_login import BCSCInvitationLoginPage
from tests.pages.bcsc_login import BCSCLoginPage
from tests.utilities.session_storage import SessionStorage
from tests.utilities.settings import get_settings, load_data_from_csv
from tests.utilities.testing_config import TestedUser, TestingConfig


def make_dir(filepath) -> bool:
    """ Make a directory.

    Returns:
        True if successful, False if not.
    """
    try:
        os.mkdir(filepath)
        return True
    except FileExistsError:
        return False


@pytest.fixture(scope='function')
def fake() -> Faker:
    """ A basic instance of Faker to make test data."""
    return Faker()


@pytest.fixture(scope='function')
def api():
    """ A basic instance of Requests to make HTTP API calls. """
    return requests


@pytest.fixture(scope='session', autouse=True)
def project_root() -> str:
    """ The Project (or Workspace) root as a filepath.

    * This conftest.py file should be in the Project Root if not already.
    """
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope='session', autouse=True)
def test_run(project_root, request) -> str:
    """ Creates the `/test_results` directory to store the results of the Test Run.

    Returns:
        The `/test_results` directory as a filepath (str).
    """
    #session = request.node
    test_results_dir = f'{project_root}/test_results'

    if os.path.exists(test_results_dir):
        # delete /test_results from previous Test Run
        shutil.rmtree(test_results_dir, ignore_errors=True)
    if not os.path.exists(test_results_dir):
        # create /test_results for this Test Run
        make_dir(test_results_dir)

    # for test in session.items:
        # make the test_result directory for each test
        # make_dir(f'{test_results_dir}/{test.name}')

    return test_results_dir


@pytest.fixture('session')
def py_config(project_root, request) -> PyleniumConfig:
    """ Initialize a PyleniumConfig for each test

    1. This starts by deserializing the user-created pylenium.json from the Project Root.
    2. If that file is not found, then proceed with Pylenium Defaults.
    3. Then any CLI arguments override their respective key/values.
    """
    try:
        # 1. Load pylenium.json in Project Root, if available
        with open(f'{project_root}/pylenium.json') as file:
            _json = json.load(file)
        config = PyleniumConfig(**_json)
    except FileNotFoundError:
        # pylenium.json not found, proceed with defaults
        config = PyleniumConfig()

    # Override with any CLI args/options
    # Driver Settings
    cli_remote_url = request.config.getoption('--remote_url')
    if cli_remote_url:
        config.driver.remote_url = cli_remote_url

    cli_browser_options = request.config.getoption('--options')
    if cli_browser_options:
        config.driver.options = [option.strip() for option in cli_browser_options.split(',')]

    cli_browser = request.config.getoption('--browser')
    if cli_browser:
        config.driver.browser = cli_browser

    cli_capabilities = request.config.getoption('--caps')
    if cli_capabilities:
        # --caps must be in '{"name": "value", "boolean": true}' format
        # with double quotes around each key. booleans are lowercase.
        config.driver.capabilities = json.loads(cli_capabilities)

    cli_page_wait_time = request.config.getoption('--page_load_wait_time')
    if cli_page_wait_time and cli_page_wait_time.isdigit():
        config.driver.page_load_wait_time = int(cli_page_wait_time)

    # Logging Settings
    cli_pylog_level = request.config.getoption('--pylog_level')
    if cli_pylog_level:
        config.logging.pylog_level = cli_pylog_level

    cli_screenshots_on = request.config.getoption('--screenshots_on')
    if cli_screenshots_on:
        shots_on = True if cli_screenshots_on.lower() == 'true' else False
        config.logging.screenshots_on = shots_on

    cli_extensions = request.config.getoption('--extensions')
    if cli_extensions:
        config.driver.extension_paths = [ext.strip() for ext in cli_extensions.split(',')]

    return config


@pytest.fixture(scope='session', autouse=True)
def logger(test_run, py_config, request) -> Logger:
    """ Manages data pertaining to the currently running Test Function or Case.

        * Creates the test-specific logger.

    Args:
        test_run: The Test Run (or Session) this test is connected to.

    Returns:
        An instance of Logger.
    """
    test_name = request.node.name
    test_result_path = f'{test_run}'

    return Logger(test_name, test_result_path, py_config.logging.pylog_level)


@pytest.fixture(scope='session')
def test_case(test_run, py_config, logger, request) -> TestCase:
    """ Manages data pertaining to the currently running Test Function or Case.

        * Creates the test-specific logger.

    Args:
        test_run: The Test Run (or Session) this test is connected to.

    Returns:
        An instance of TestCase.
    """
    test_name = request.node.name
    test_result_path = f'{test_run}'
    py_config.driver.capabilities.update({'name': test_name})

    test = {
        'name': test_name,
        'file_path': test_result_path,
        'logger': logger
    }
    return TestCase(**test)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """ Yield each test's outcome so we can handle it in other fixtures. """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep


@pytest.fixture(scope='session')
def selenium(docker_services):
    """Spin up a keycloak instance and initialize jwt."""
    docker_services.start('selenium-hub')
    docker_services.start('chrome')
    docker_services.start('firefox')
    time.sleep(30)
    docker_services.wait_for_service('selenium-hub', 4444)


@pytest.fixture(scope='session')
def docker_compose_files(pytestconfig):
    """Get the docker-compose.yml absolute path."""
    import os
    return [
        os.path.join(str(pytestconfig.rootdir), 'tests/docker', 'docker-compose.yml')
    ]


def pytest_addoption(parser):
    parser.addoption(
        '--browser', action='store', default='', help='The lowercase browser name: chrome | firefox'
    )
    parser.addoption(
        '--remote_url', action='store', default='', help='Grid URL to connect tests to.'
    )
    parser.addoption(
        '--screenshots_on', action='store', default='', help="Should screenshots be saved? true | false"
    )
    parser.addoption(
        '--pylog_level', action='store', default='', help="Set the pylog_level: 'off' | 'info' | 'debug'"
    )
    parser.addoption(
        '--options', action='store',
        default='', help='Comma-separated list of Browser Options. Ex. "headless, incognito"'
    )
    parser.addoption(
        '--caps', action='store',
        default='', help='List of key-value pairs. Ex. \'{"name": "value", "boolean": true}\''
    )

    parser.addoption(
        '--page_load_wait_time', action='store',
        default='', help='The amount of time to wait for a page load before raising an error. Default is 0.'
    )
    parser.addoption(
        '--extensions', action='store',
        default='', help='Comma-separated list of extension paths. Ex. "*.crx, *.crx"'
    )


try:
    pytest.skip()
except BaseException as e:
    Skipped = type(e)

try:
    pytest.xfail()
except BaseException as e:
    XFailed = type(e)


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            if call.excinfo.type in {Skipped, XFailed}:
                return

            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    previousfailed = getattr(item.parent, "_previousfailed", None)
    if previousfailed is not None:
        pytest.xfail("previous test failed (%s)" % previousfailed.name)


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


@pytest.fixture(autouse=True)
def skip_by_org_type(testing_config, request):
    """Skip test case by org(account) type."""
    if request.node.get_closest_marker('skip_org_type'):
        if request.node.get_closest_marker('skip_org_type').args[0] == testing_config.org_type:
            pytest.skip('skipped on org(account) type: {}'.format(testing_config.org_type))


@pytest.fixture(autouse=True)
def skip_by_access_type(testing_config, request):
    """Skip test case by access type."""
    if request.node.get_closest_marker('skip_login_as'):
        if request.node.get_closest_marker('skip_login_as').args[0] == testing_config.login_as:
            pytest.skip('skipped on access type: {}'.format(testing_config.login_as))


@pytest.fixture(autouse=True)
def skip_by_paybc_status(testing_config, request):
    """Skip test case by paybc_status."""
    if request.node.get_closest_marker('skip_paybc_status'):
        if request.node.get_closest_marker('skip_paybc_status').args[0] == testing_config.paybc_status:
            pytest.skip('skipped on paybc status: {}'.format(testing_config.paybc_status))


@pytest.fixture(autouse=True)
def skip_by_payment_status(testing_config, request):
    """Skip test case by paybc_status."""
    if request.node.get_closest_marker('skip_payment_status'):
        if request.node.get_closest_marker('skip_payment_status').args[0] != testing_config.payment_status:
            pytest.skip('skipped on payment status: {}'.format(testing_config.payment_status))

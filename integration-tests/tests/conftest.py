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
import logging
import os
import shutil
import sys
import time

import pytest
import requests
from faker import Faker
from pytest_reportportal import RPLogger, RPLogHandler

from pylenium import Pylenium
from pylenium.config import PyleniumConfig, TestCase


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


@pytest.fixture(scope="session")
def logger(request):
    """ Report Portal Logger """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # Create handler for Report Portal if the service has been
    # configured and started.
    if hasattr(request.node.config, 'py_test_service'):
        # Import Report Portal logger and handler to the test module.
        logging.setLoggerClass(RPLogger)
        rp_handler = RPLogHandler(request.node.config.py_test_service)
        # Add additional handlers if it is necessary
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
    else:
        rp_handler = logging.StreamHandler(sys.stdout)
    # Set INFO level for Report Portal handler.
    rp_handler.setLevel(logging.INFO)
    return logger


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
    session = request.node
    test_results_dir = f'{project_root}/test_results'

    if os.path.exists(test_results_dir):
        # delete /test_results from previous Test Run
        shutil.rmtree(test_results_dir, ignore_errors=True)
    if not os.path.exists(test_results_dir):
        # create /test_results for this Test Run
        make_dir(test_results_dir)

    for test in session.items:
        # make the test_result directory for each test
        make_dir(f'{test_results_dir}/{test.name}')

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
        # 2. pylenium.json not found, proceed with defaults
        config = PyleniumConfig()

    # 3. Override with any CLI args/options
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


@pytest.fixture(scope='session')
def test_case(test_run, py_config, request) -> TestCase:
    """ Manages data pertaining to the currently running Test Function or Case.
        * Creates the test-specific logger.
    Args:
        test_run: The Test Run (or Session) this test is connected to.
    Returns:
        An instance of TestCase.
    """
    test_name = request.node.name
    test_result_path = f'{test_run}/{test_name}'
    py_config.driver.capabilities.update({'name': test_name})
    return TestCase(name=test_name, file_path=test_result_path)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """ Yield each test's outcome so we can handle it in other fixtures. """
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call':
        setattr(item, "report", report)
    return report


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


pytest_plugins = [
    'tests.fixtures.setup_data',
    'tests.fixtures.skip_marker'
]

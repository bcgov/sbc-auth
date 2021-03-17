import pytest


@pytest.fixture(autouse=True)
def skip_if_org_type(testing_config, request):
    """Skip test case by org(account) type."""
    if request.node.get_closest_marker('skip_org_type'):
        if request.node.get_closest_marker('skip_org_type').args[0] == testing_config.org_type:
            pytest.skip('skipped on org(account) type: {}'.format(testing_config.org_type))


@pytest.fixture(autouse=True)
def skip_if_login_as(testing_config, request):
    """Skip test case by access type."""
    if request.node.get_closest_marker('skip_login_as'):
        if request.node.get_closest_marker('skip_login_as').args[0] == testing_config.login_as:
            pytest.skip('skipped on login as: {}'.format(testing_config.login_as))


@pytest.fixture(autouse=True)
def skip_if_access_type(testing_config, request):
    """Skip test case by access type."""
    if request.node.get_closest_marker('skip_access_type'):
        if request.node.get_closest_marker('skip_access_type').args[0] == testing_config.access_type:
            pytest.skip('skipped on access type: {}'.format(testing_config.access_type))


@pytest.fixture(autouse=True)
def skip_if_paybc_status(testing_config, request):
    """Skip test case by paybc_status."""
    if request.node.get_closest_marker('skip_paybc_status'):
        if request.node.get_closest_marker('skip_paybc_status').args[0] == testing_config.paybc_status:
            pytest.skip('skipped on paybc status: {}'.format(testing_config.paybc_status))


@pytest.fixture(autouse=True)
def skip_if_payment_status(testing_config, request):
    """Skip test case by paybc_status."""
    if request.node.get_closest_marker('skip_payment_status'):
        if request.node.get_closest_marker('skip_payment_status').args[0] != testing_config.payment_status:
            pytest.skip('skipped on payment status: {}'.format(testing_config.payment_status))

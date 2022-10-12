# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test-Suite to ensure that the Flag Service is working as expected."""
import pytest
from flask import Flask

from auth_api.services import Flags
from auth_api.models import User

app = None


@pytest.fixture
def setup():
    """Initialize app with dev env for testing."""
    global app
    app = Flask(__name__)
    app.env = 'development'


def test_flags_constructor_no_app(setup):
    """Ensure that flag object can be initialized."""
    flags = Flags()
    assert flags


def test_flags_constructor_with_app(setup):
    """Ensure that extensions can be initialized."""
    with app.app_context():
        flags = Flags(app)
    assert flags
    assert app.extensions['featureflags']


def test_init_app_dev_with_key(setup):
    """Ensure that extension can be initialized with a key in dev."""
    app.config['AUTH_LD_SDK_KEY'] = 'https://no.flag/avail'

    with app.app_context():
        flags = Flags()
        flags.init_app(app)
    assert flags
    assert app.extensions['featureflags']
    assert app.extensions['featureflags'].get_sdk_key() == 'https://no.flag/avail'


def test_init_app_dev_no_key(setup):
    """Ensure that extension can be initialized with no key in dev."""
    app.config['AUTH_LD_SDK_KEY'] = None

    with app.app_context():
        flags = Flags()
        flags.init_app(app)
    assert flags
    assert app.extensions['featureflags']


def test_init_app_prod_with_key(setup):
    """Ensure that extension can be initialized with a key in prod."""
    app.env = 'production'
    app.config['AUTH_LD_SDK_KEY'] = 'https://no.flag/avail'

    with app.app_context():
        flags = Flags()
        flags.init_app(app)
    assert flags
    assert app.extensions['featureflags']
    assert app.extensions['featureflags'].get_sdk_key() == 'https://no.flag/avail'


def test_init_app_prod_no_key(setup):
    """Ensure that extension can be initialized with no key in prod."""
    app.env = 'production'
    app.config['AUTH_LD_SDK_KEY'] = None

    with app.app_context():
        flags = Flags()
        flags.init_app(app)
        with pytest.raises(KeyError):
            client = app.extensions['featureflags']
            assert not client
    assert flags


@pytest.mark.parametrize('test_name,flag_name,expected', [
    ('boolean flag', 'bool-flag', True),
    ('string flag', 'string-flag', 'a string value'),
    ('integer flag', 'integer-flag', 10),
])
def test_flags_read_from_json(setup, test_name, flag_name, expected):
    """Ensure that is_on is TRUE when reading flags from local JSON file."""
    app.config['AUTH_LD_SDK_KEY'] = 'https://no.flag/avail'

    with app.app_context():
        flags = Flags()
        flags.init_app(app)

        assert flags.is_on(flag_name)


def test_flags_read_from_json_missing_flag(setup):
    """Ensure that is_on is FALSE when reading a flag that doesn't exist from local JSON file."""
    app.config['AUTH_LD_SDK_KEY'] = 'https://no.flag/avail'

    with app.app_context():
        flags = Flags()
        flags.init_app(app)
        flag_on = flags.is_on('missing flag')

    assert not flag_on


@pytest.mark.parametrize('test_name,flag_name,expected', [
    ('boolean flag', 'bool-flag', True),
    ('string flag', 'string-flag', 'a string value'),
    ('integer flag', 'integer-flag', 10),
])
def test_flags_read_flag_values_from_json(setup, test_name, flag_name, expected):
    """Ensure that values read from JSON == expected values when no user is passed."""
    app.config['AUTH_LD_SDK_KEY'] = 'https://no.flag/avail'

    with app.app_context():
        flags = Flags()
        flags.init_app(app)
        val = flags.value(flag_name)

    assert val == expected


@pytest.mark.parametrize('test_name,flag_name,expected', [
    ('boolean flag', 'bool-flag', True),
    ('string flag', 'string-flag', 'a string value'),
    ('integer flag', 'integer-flag', 10),
])
def test_flags_read_flag_values_unique_user(setup, test_name, flag_name, expected):
    """Ensure that values read from JSON == expected values when passed with a user."""
    app.config['AUTH_LD_SDK_KEY'] = 'https://no.flag/avail'

    user = User(username='username', firstname='firstname', lastname='lastname', idp_userid='userid')
    with app.app_context():
        flags = Flags()
        flags.init_app(app)
        val = flags.value(flag_name, user)
        flag_on = flags.is_on(flag_name, user)

    assert val == expected
    assert flag_on

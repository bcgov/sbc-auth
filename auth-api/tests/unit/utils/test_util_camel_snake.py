# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests to assure the CORS utilities.

Test-Suite to ensure that the CORS decorator is working as expected.
"""
from auth_api.utils.util import camelback2snake, snake2camelback


TEST_CAMEL_DATA = {'loginSource': 'PASSCODE', 'userName': 'test name', 'realmAccess': {
    'roles': ['basic']
}}


TEST_SNAKE_DATA = {'login_source': 'PASSCODE', 'user_name': 'test name', 'realm_access': {
    'roles': ['basic']
}}


def test_camelback2snake():
    """Assert that the options methos is added to the class and that the correct access controls are set."""
    snake = camelback2snake(TEST_CAMEL_DATA)

    assert snake['login_source'] == TEST_SNAKE_DATA['login_source']


def test_snake2camelback():
    """Assert that the options methos is added to the class and that the correct access controls are set."""
    camel = snake2camelback(TEST_SNAKE_DATA)

    assert camel['loginSource'] == TEST_CAMEL_DATA['loginSource']

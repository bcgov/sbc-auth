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

import base64
from urllib.parse import unquote

import pytest

from auth_api.utils.util import (
    camelback2snake,
    escape_wam_friendly_url,
    safe_int,
    snake2camelback,
)

TEST_CAMEL_DATA = {"loginSource": "PASSCODE", "userName": "test name", "realmAccess": {"roles": ["basic"]}}

TEST_SNAKE_DATA = {"login_source": "PASSCODE", "user_name": "test name", "realm_access": {"roles": ["basic"]}}


def test_camelback2snake():
    """Assert that the options methos is added to the class and that the correct access controls are set."""
    snake = camelback2snake(TEST_CAMEL_DATA)

    assert snake["login_source"] == TEST_SNAKE_DATA["login_source"]


def test_snake2camelback():
    """Assert that the options methos is added to the class and that the correct access controls are set."""
    camel = snake2camelback(TEST_SNAKE_DATA)

    assert camel["loginSource"] == TEST_CAMEL_DATA["loginSource"]


@pytest.mark.parametrize(
    "test_input,expected", [("foo", "Zm9v"), ("foo-bar", "Zm9vLWJhcg%3D%3D"), ("foo bar.....", "Zm9vIGJhci4uLi4u")]
)
def test_escape_wam_friendly_url_multiple(test_input, expected):
    """Assert manually calculated url encodings."""
    assert escape_wam_friendly_url(test_input) == expected


def test_escape_wam_friendly_url():
    """Assert conversion back yields same string."""
    org_name = "foo-bar helo .."
    org_name_encoded = escape_wam_friendly_url(org_name)
    param1 = unquote(org_name_encoded)
    org_name_actual = base64.b64decode(bytes(param1, encoding="utf-8")).decode("utf-8")
    assert org_name_actual == org_name


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (123, 123),
        ("123", 123),
        ("undefined", -1),
        (None, -1),
        ("", -1),
        ("invalid", -1),
        (45.67, -1),
        ("456", 456),
        (0, 0),
        ("0", 0),
    ],
)
def test_safe_int_default(test_input, expected):
    """Assert that safe_int converts values correctly with default -1."""
    assert safe_int(test_input) == expected


@pytest.mark.parametrize(
    "test_input,default,expected",
    [
        (123, 999, 123),
        ("123", 999, 123),
        ("undefined", 999, 999),
        (None, 999, 999),
        ("", 999, 999),
        ("invalid", 0, 0),
        ("789", 100, 789),
    ],
)
def test_safe_int_custom_default(test_input, default, expected):
    """Assert that safe_int converts values correctly with custom default."""
    assert safe_int(test_input, default) == expected

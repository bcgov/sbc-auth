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

"""Tests to assure the passcode hashing utilities.

Test-Suite to ensure that the passcode hashing is working as expected.
"""
from auth_api.utils import passcode


def test_passcode_hash():
    """Assert that passcode can be hashed."""
    pass_code: str = "111111111"
    hashed_pass_code: str = passcode.passcode_hash(pass_code)
    assert hashed_pass_code


def test_passcode_hash_fail():
    """Assert that passcode can be hash."""
    pass_code: str = None
    hashed_pass_code: str = passcode.passcode_hash(pass_code)
    assert hashed_pass_code is None


def test_passcode_hash_different():
    """Assert that the same passcode get different hash value by multiple running."""
    pass_code: str = "111111111"
    hashed_pass_code: str = passcode.passcode_hash(pass_code)
    hashed_pass_code2: str = passcode.passcode_hash(pass_code)
    assert hashed_pass_code != hashed_pass_code2


def test_validate_passcode():
    """Assert that passcode can be validate."""
    pass_code: str = "111111111"
    hashed_pass_code: str = passcode.passcode_hash(pass_code)
    checked_pass_code: str = "111111111"
    validated: bool = passcode.validate_passcode(checked_pass_code, hashed_pass_code)
    assert validated


def test_validate_passcode_empty_input():
    """Assert that passcode can be validate."""
    pass_code: str = "111111111"
    hashed_pass_code: str = passcode.passcode_hash(pass_code)
    checked_pass_code: str = None
    validated: bool = passcode.validate_passcode(checked_pass_code, hashed_pass_code)
    assert not validated


def test_validate_passcode_fail():
    """Assert that passcode can be validate."""
    pass_code: str = "111111111"
    hashed_pass_code: str = passcode.passcode_hash(pass_code)
    checked_pass_code: str = "222222222"
    validated: bool = passcode.validate_passcode(checked_pass_code, hashed_pass_code)
    assert not validated

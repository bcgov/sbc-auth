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
"""Using the bcrypt library to securely hash and check hashed passcode."""

import bcrypt


def passcode_hash(passcode: str):
    """Return hashed passcode."""
    if passcode:
        hashed_passcode: bytes = bcrypt.hashpw(passcode.encode(), bcrypt.gensalt())
        return hashed_passcode.decode()
    return None


def validate_passcode(passcode: str, hashed_passcode: str):
    """Validate passcode and hashed passcode."""
    if passcode and hashed_passcode:
        passcode_bytes: str = passcode.encode()
        hashed_passcod_bytes: bytes = hashed_passcode.encode()
        return bcrypt.checkpw(passcode_bytes, hashed_passcod_bytes)
    return False

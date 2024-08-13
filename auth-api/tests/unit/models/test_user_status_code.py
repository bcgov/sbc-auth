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
"""Tests for the user_status_code model.

Test suite to ensure that the user_status_code model routines are working as expected.
"""

from auth_api.models import UserStatusCode as UserStatusCodeModel


def test_status_code(session):
    """Assert that a User Status Code can be stored in the database."""
    status_code = UserStatusCodeModel(id=100, name="TEST", description="TEST CODE")
    status_code = status_code.save()
    assert status_code.id is not None
    status_code = UserStatusCodeModel.get_user_status_by_name("TEST")
    assert status_code.id == 100
    assert UserStatusCodeModel.get_default_type() == 1

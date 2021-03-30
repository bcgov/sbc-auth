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
"""Tests for the StaffTask service.

Test suite to ensure that the Staff Task service routines are working as expected.
"""

from auth_api.services import StaffTask as StaffTaskService
from tests.utilities.factory_utils import factory_staff_task_service


def test_fetch_staff_tasks(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that staff tasks can be fetched."""
    staff_task = factory_staff_task_service()
    dictionary = staff_task.as_dict()
    name = dictionary['name']

    fetched_staff_task = StaffTaskService.fetch_staff_tasks()

    assert fetched_staff_task
    assert fetched_staff_task
    for item in fetched_staff_task:
        assert item['name'] == name

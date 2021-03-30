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
"""Tests for the StaffTask model.

Test suite to ensure that the Staff Task model routines are working as expected.
"""

from _datetime import datetime, timedelta

from auth_api.models import StaffTask as StaffTaskModel


def test_staff_task_model(session):
    """Assert that an Entity can be stored in the service."""
    staff_task = StaffTaskModel(name='TEST', date_submitted=datetime.now(), relationship_type='Org',
                                relationship_id=10, task_type='Pending Review')

    session.add(staff_task)
    session.commit()
    assert staff_task.id is not None
    assert staff_task.name == 'TEST'


def test_staff_task_model_with_due_date(session):
    """Assert that an Entity can be stored in the service."""
    staff_task = StaffTaskModel(name='TEST', date_submitted=datetime.now(), relationship_type='Org',
                                relationship_id=10, task_type='Pending Review', due_date=datetime.now())

    session.add(staff_task)
    session.commit()
    assert staff_task.id is not None
    assert staff_task.name == 'TEST'
    assert staff_task.due_date is not None


def test_fetch_staff_tasks(session):  # pylint:disable=unused-argument
    """Assert that we can fetch all staff tasks."""
    staff_task = StaffTaskModel(name='TEST', date_submitted=datetime.now(), relationship_type='Org',
                                relationship_id=10, task_type='Pending Review', due_date=datetime.now())
    session.add(staff_task)
    session.commit()

    found_staff_tasks = StaffTaskModel.fetch_staff_tasks()
    assert found_staff_tasks

    for found_staff_task in found_staff_tasks:
        assert found_staff_task.name == staff_task.name

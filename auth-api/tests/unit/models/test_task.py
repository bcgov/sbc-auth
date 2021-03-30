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
"""Tests for the Task model.

Test suite to ensure that the Staff Task model routines are working as expected.
"""

from _datetime import datetime

from auth_api.models import Task as TaskModel


def test_task_model(session):
    """Assert that a task can be stored in the service."""
    task = TaskModel(name='TEST', date_submitted=datetime.now(), relationship_type='Org',
                     relationship_id=10, task_type='Pending Review', task_status='Pending')

    session.add(task)
    session.commit()
    assert task.id is not None
    assert task.name == 'TEST'


def test_task_model_with_due_date(session):
    """Assert that a task can be stored in the service."""
    task = TaskModel(name='TEST', date_submitted=datetime.now(), relationship_type='Org',
                     relationship_id=10, task_type='Pending Review', due_date=datetime.now(), task_status='Pending')

    session.add(task)
    session.commit()
    assert task.id is not None
    assert task.name == 'TEST'
    assert task.due_date is not None


def test_fetch_tasks(session):  # pylint:disable=unused-argument
    """Assert that we can fetch all tasks."""
    task = TaskModel(name='TEST', date_submitted=datetime.now(), relationship_type='Org',
                     relationship_id=10, task_type='Pending Review', due_date=datetime.now(), task_status='Pending')
    session.add(task)
    session.commit()

    found_tasks = TaskModel.fetch_tasks()
    assert found_tasks

    for found_staff_task in found_tasks:
        assert found_staff_task.name == task.name

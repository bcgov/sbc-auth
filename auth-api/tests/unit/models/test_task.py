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
from auth_api.utils.enums import TaskRelationshipType, TaskStatus, TaskRelationshipStatus, TaskTypePrefix
from tests.utilities.factory_utils import factory_user_model, factory_task_models


def test_task_model(session):
    """Assert that a task can be stored in the service."""
    user = factory_user_model()
    task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
    task = TaskModel(name='TEST', date_submitted=datetime.now(), relationship_type=TaskRelationshipType.ORG.value,
                     relationship_id=10, type=task_type, status=TaskStatus.OPEN.value,
                     related_to=user.id)

    session.add(task)
    session.commit()
    assert task.id is not None
    assert task.name == 'TEST'


def test_task_model_with_due_date(session):
    """Assert that a task can be stored in the service."""
    user = factory_user_model()
    task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
    task = TaskModel(name='TEST', date_submitted=datetime.now(), relationship_type=TaskRelationshipType.ORG.value,
                     relationship_id=10, type=task_type, due_date=datetime.now(),
                     status=TaskStatus.OPEN.value, related_to=user.id)

    session.add(task)
    session.commit()
    assert task.id is not None
    assert task.name == 'TEST'
    assert task.due_date is not None


def test_fetch_tasks(session):  # pylint:disable=unused-argument
    """Assert that we can fetch all tasks."""
    user = factory_user_model()
    task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
    task = TaskModel(name='TEST', date_submitted=datetime.now(), relationship_type=TaskRelationshipType.ORG.value,
                     relationship_id=10, type=task_type, due_date=datetime.now(),
                     status=TaskStatus.OPEN.value, related_to=user.id,
                     relationship_status=TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
                     )
    session.add(task)
    session.commit()
    found_tasks, count = TaskModel.fetch_tasks(
        task_relationship_status=TaskRelationshipStatus.PENDING_STAFF_REVIEW.value,
        task_type=task_type,
        task_status=TaskStatus.OPEN.value,
        page=1, limit=10)
    assert found_tasks
    assert count == 1

    for found_staff_task in found_tasks:
        assert found_staff_task.name == task.name


def test_find_task_by_id(session):  # pylint:disable=unused-argument
    """Assert that we can fetch all tasks."""
    user = factory_user_model()
    task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
    task = TaskModel(name='TEST', date_submitted=datetime.now(), relationship_type=TaskRelationshipType.ORG.value,
                     relationship_id=10, type=task_type, due_date=datetime.now(),
                     status=TaskStatus.OPEN.value, related_to=user.id)
    session.add(task)
    session.commit()
    found_task = TaskModel.find_by_task_id(task.id)
    assert found_task
    assert found_task.name == task.name


def test_fetch_tasks_pagination(session):  # pylint:disable=unused-argument
    """Assert that we can fetch all tasks."""
    user = factory_user_model()
    factory_task_models(6, user.id)
    task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value

    found_tasks, count = TaskModel.fetch_tasks(
        task_relationship_status=TaskRelationshipStatus.PENDING_STAFF_REVIEW.value,
        task_type=task_type,
        task_status=TaskStatus.OPEN.value, page=3, limit=2)
    assert found_tasks
    assert count == 6


def test_task_model_account_id(session):
    """Assert that a task can be stored along with account id column."""
    user = factory_user_model()
    task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
    task = TaskModel(name='TEST', date_submitted=datetime.now(), relationship_type=TaskRelationshipType.ORG.value,
                     relationship_id=10, type=task_type, status=TaskStatus.OPEN.value,
                     account_id=10, related_to=user.id)

    session.add(task)
    session.commit()
    assert task.id is not None
    assert task.name == 'TEST'
    assert task.account_id == 10

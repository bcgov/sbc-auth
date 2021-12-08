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
from auth_api.utils.enums import TaskRelationshipStatus, TaskRelationshipType, TaskStatus, TaskTypePrefix
from tests.utilities.factory_utils import factory_task_models, factory_user_model


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
        task_status=[TaskStatus.OPEN.value],
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
        task_status=[TaskStatus.OPEN.value], page=3, limit=2)
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


def test_fetch_pending_tasks_descending(session):  # pylint:disable=unused-argument
    """Assert that we can fetch all tasks."""
    user = factory_user_model()
    task = TaskModel(name='TEST 1', date_submitted=datetime.now(),
                     relationship_type=TaskRelationshipType.ORG.value,
                     relationship_id=10, type=TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value,
                     status=TaskStatus.OPEN.value,
                     related_to=user.id,
                     relationship_status=TaskRelationshipStatus.PENDING_STAFF_REVIEW.value)
    task.save()
    task = TaskModel(name='TEST 2', date_submitted=datetime(2021, 5, 25),
                     relationship_type=TaskRelationshipType.ORG.value,
                     relationship_id=10, type=TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value,
                     status=TaskStatus.OPEN.value,
                     related_to=user.id,
                     relationship_status=TaskRelationshipStatus.PENDING_STAFF_REVIEW.value)
    task.save()
    task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value

    found_tasks, count = TaskModel.fetch_tasks(
        task_relationship_status=TaskRelationshipStatus.PENDING_STAFF_REVIEW.value,
        task_type=task_type,
        task_status=[TaskStatus.OPEN.value], page=1, limit=2)
    assert found_tasks
    assert found_tasks[0].name == 'TEST 2'
    assert found_tasks[1].name == 'TEST 1'
    assert count == 2


def test_finding_task_by_relationship_id(session):  # pylint:disable=unused-argument
    """Assert that we can fetch all tasks."""
    user = factory_user_model()
    task = TaskModel(name='TEST 1', date_submitted=datetime.now(),
                     relationship_type=TaskRelationshipType.ORG.value,
                     relationship_id=10, type=TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value,
                     status=TaskStatus.OPEN.value,
                     related_to=user.id,
                     relationship_status=TaskRelationshipStatus.PENDING_STAFF_REVIEW.value)
    task.save()

    found_task = TaskModel.find_by_task_relationship_id(
        task_relationship_type=TaskRelationshipType.ORG.value, relationship_id=10)
    assert found_task
    assert found_task.name == 'TEST 1'
    assert found_task.relationship_id == 10
    assert found_task.status == TaskStatus.OPEN.value


def test_find_by_task_for_user(session):  # pylint:disable=unused-argument
    """Assert that we can fetch all tasks."""
    user = factory_user_model()
    task = TaskModel(name='TEST 1', date_submitted=datetime.now(),
                     relationship_type=TaskRelationshipType.USER.value,
                     relationship_id=user.id, type=TaskTypePrefix.BCEID_ADMIN.value,
                     status=TaskStatus.OPEN.value,
                     related_to=user.id,
                     account_id=10,
                     relationship_status=TaskRelationshipStatus.PENDING_STAFF_REVIEW.value)
    task.save()

    found_task = TaskModel.find_by_task_for_user(org_id=10, status=TaskStatus.OPEN.value)
    assert found_task
    assert found_task.name == 'TEST 1'
    assert found_task.relationship_id == user.id
    assert found_task.status == TaskStatus.OPEN.value

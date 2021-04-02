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
"""Tests for the Task service.

Test suite to ensure that the Task service routines are working as expected.
"""

from auth_api.services import Task as TaskService
from auth_api.utils.enums import TaskRelationshipType
from tests.utilities.factory_utils import factory_task_service, factory_org_model, factory_user_model


def test_fetch_tasks(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that tasks can be fetched."""
    user = factory_user_model()
    task = factory_task_service(user.id)
    dictionary = task.as_dict()
    name = dictionary['name']

    fetched_task = TaskService.fetch_tasks(task_relationship_type=TaskRelationshipType.ORG.value)

    assert fetched_task
    for item in fetched_task:
        assert item.name == name


def test_create_task(session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a task can be created."""
    test_org = factory_org_model()
    test_task_info = ({
                    'relationshipName': test_org.name,
                    'relationshipId': test_org.id
    })
    task = TaskService.create_task(test_task_info)
    assert task
    dictionary = task.as_dict()
    assert dictionary['name'] == test_org.name

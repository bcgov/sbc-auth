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
"""The Task service.

This module manages the tasks.
"""
from datetime import datetime
from typing import Dict
from flask import current_app

from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.models import Task as TaskModel
from auth_api.models import User as UserModel
from auth_api.schemas import TaskSchema
from auth_api.utils.enums import TaskRelationshipType, TaskStatus, TaskType
from auth_api.utils.util import camelback2snake

ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Task:  # pylint: disable=too-many-instance-attributes
    """Manages all aspects of the Task Entity.

    This manages storing the Task in the cache,
    ensuring that the local cache is up to date,
    submitting changes back to all storage systems as needed.
    """

    def __init__(self, model):
        """Return a Task service."""
        self._model: TaskModel = model

    @property
    def identifier(self):
        """Return the identifier for this user."""
        return self._model.id

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the Task as a python dict.

        None fields are not included in the dict.
        """
        task_schema = TaskSchema()
        obj = task_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    def create_task(org_info: dict):
        """Create a new task record."""
        current_app.logger.debug('<create_task ')
        task_model = TaskModel(name=org_info.get('name'),
                               date_submitted=datetime.today(),
                               relationship_type=TaskRelationshipType.ORG.value,
                               relationship_id=org_info.get('relationshipId'),
                               type=TaskType.PENDING_STAFF_REVIEW.value,
                               status=TaskStatus.OPEN.value,
                               related_to=org_info.get('relatedTo'))
        task_model.save()
        return Task(task_model)

    def update_task(self, task_info: Dict = None, token_info: Dict = None):
        """Update a task record."""
        current_app.logger.debug('<update_task ')
        task_model: TaskModel = self._model

        user: UserModel = UserModel.find_by_jwt_token(token=token_info)
        task_model.update_from_dict(**camelback2snake(task_info))
        task_model.decision_made_by = user.username

        task_model.save()
        return Task(task_model)

    @staticmethod
    def fetch_tasks(task_type: str):
        """Fetch all tasks."""
        if not any(e.value == task_type for e in TaskType):
            return []

        current_app.logger.debug('<fetch_tasks ')
        tasks = TaskModel.fetch_tasks(task_type)
        tasks_response = []

        for task in tasks:
            tasks_response.append(task)

        return tasks_response

    @staticmethod
    def find_by_task_id(task_id):
        """Find and return an existing task with the provided id."""
        if task_id is None:
            return None

        task_model = TaskModel.find_by_task_id(task_id)
        if not task_model:
            return None

        return Task(task_model)

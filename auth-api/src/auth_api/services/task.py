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

from flask import current_app
from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.models import Task as TaskModel
from auth_api.schemas import TaskSchema

ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Task:  # pylint: disable=too-many-instance-attributes
    """Manages all aspects of the Task Entity.

    This manages storing the Task in the cache,
    ensuring that the local cache is up to date,
    submitting changes back to all storage systems as needed.
    """

    def __init__(self, model):
        """Return a Task object."""
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
    def create_task(task_model: TaskModel):
        """Create a new task record."""
        current_app.logger.debug('<create_staff_task ')

        task_model.add_to_session()
        task_model.save()

        return Task(task_model)

    @staticmethod
    def fetch_tasks():
        """Fetch all tasks."""
        tasks = TaskModel.fetch_tasks()
        tasks_response = []

        for task in tasks:
            tasks_response.append(Task(task).as_dict())

        return tasks_response

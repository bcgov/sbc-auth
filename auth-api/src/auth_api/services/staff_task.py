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
"""The Staff Task service.

This module manages the staff tasks.
"""

from typing import Dict, List

from flask import current_app
from requests import HTTPError
from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.models import StaffTask as StaffTaskModel
from auth_api.schemas import StaffTaskSchema
from auth_api.utils.util import camelback2snake

ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class StaffTask:  # pylint: disable=too-many-instance-attributes
    """Manages all aspects of the Staff Task Entity.

    This manages storing the Staff Task in the cache,
    ensuring that the local cache is up to date,
    submitting changes back to all storage systems as needed.
    """

    def __init__(self, model):
        """Return a Staff Task object."""
        self._model: StaffTaskModel = model

    @property
    def identifier(self):
        """Return the identifier for this user."""
        return self._model.id

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the Staff Task as a python dict.

        None fields are not included in the dict.
        """
        staff_task_schema = StaffTaskSchema()
        obj = staff_task_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    def create_staff_task(staff_task_model: StaffTaskModel):
        """Create a new staff task record."""
        current_app.logger.debug('<create_staff_task ')

        staff_task_model.add_to_session()
        staff_task_model.save()

        return StaffTask(staff_task_model)

    @staticmethod
    def fetch_staff_tasks():
        """Fetch all staff tasks."""
        staff_tasks = StaffTaskModel.fetch_staff_tasks()
        staff_tasks_response = []

        for staff_task in staff_tasks:
            staff_tasks_response.append(StaffTask(staff_task).as_dict())

        return staff_tasks_response

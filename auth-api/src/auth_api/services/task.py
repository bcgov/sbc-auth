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
from auth_api.models import ProductSubscription as ProductSubscriptionModel
from auth_api.models import User as UserModel
from auth_api.schemas import TaskSchema
from auth_api.utils.enums import TaskType, TaskStatus, TaskRelationshipType, AffidavitStatus, \
    ProductSubscriptionStatus
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
    def create_task(task_info: dict):
        """Create a new task record."""
        current_app.logger.debug('<create_task ')
        task_model = TaskModel(**camelback2snake(task_info))
        task_model.save()
        current_app.logger.debug('>create_task ')
        return Task(task_model)

    def update_task(self, task_info: Dict = None, token_info: Dict = None, origin_url: str = None):
        """Update a task record."""
        current_app.logger.debug('<update_task ')
        task_model: TaskModel = self._model

        user: UserModel = UserModel.find_by_jwt_token(token=token_info)
        task_model.name = task_info.get('name')
        task_model.status = task_info.get('status')
        task_model.decision_made_by = user.username
        task_model.decision_made_on = datetime.now()
        task_model.save()

        # Update its relationship
        task_relationship_status = task_info.pop('relationshipStatus')
        self.update_relationship(task_relationship_status=task_relationship_status,
                                 token_info=token_info,
                                 origin_url=origin_url)
        current_app.logger.debug('>update_task ')

        return Task(task_model)

    def update_relationship(self, task_relationship_status: str, token_info: Dict = None, origin_url: str = None):
        """Retrieve the relationship record and update the status."""
        task_model: TaskModel = self._model
        current_app.logger.debug('<update_task_relationship ')

        if task_model.relationship_type == TaskRelationshipType.ORG.value:
            # Update Org relationship
            is_approved: bool = task_relationship_status == AffidavitStatus.APPROVED.value
            org_id = task_model.relationship_id
            self.update_org(is_approved=is_approved, org_id=org_id,
                            token_info=token_info,
                            origin_url=origin_url)

        elif task_model.relationship_type == TaskRelationshipType.PRODUCT.value:
            # Update Product relationship
            product_subscription_id = task_model.relationship_id
            is_approved: bool = task_relationship_status == ProductSubscriptionStatus.ACTIVE.value
            self.update_product_subscription(is_approved=is_approved, product_subscription_id=product_subscription_id)

        current_app.logger.debug('>update_task_relationship ')

    @staticmethod
    def update_org(is_approved: bool, org_id: int, token_info: Dict = None, origin_url: str = None):
        """Approve/Reject Affidavit and Org."""
        from auth_api.services import \
            Org as OrgService  # pylint:disable=cyclic-import, import-outside-toplevel
        current_app.logger.debug('<update_task_org ')

        OrgService.approve_or_reject(org_id=org_id, is_approved=is_approved,
                                     token_info=token_info,
                                     origin_url=origin_url)

        current_app.logger.debug('>update_task_org ')

    @staticmethod
    def update_product_subscription(is_approved: bool, product_subscription_id: int):
        """Review Product Subscription."""
        current_app.logger.debug('<update_task_product ')
        # Approve/Reject Product subscription
        product_subscription: ProductSubscriptionModel = ProductSubscriptionModel.find_by_id(product_subscription_id)
        if is_approved:
            product_subscription.status_code = ProductSubscriptionStatus.ACTIVE.value
        else:
            product_subscription.status_code = ProductSubscriptionStatus.REJECTED.value
        product_subscription.save()
        current_app.logger.debug('>update_task_product ')

    @staticmethod
    def fetch_tasks(**kwargs):
        """Fetch all tasks."""
        task_type = kwargs.get('task_type')
        task_status = kwargs.get('task_status')
        if not any(e.value == task_type for e in TaskType):
            return []
        if not any(e.value == task_status for e in TaskStatus):
            return []

        page: int = int(kwargs.get('page'))
        limit: int = int(kwargs.get('limit'))
        search_args = (task_type,
                       task_status,
                       page,
                       limit)

        current_app.logger.debug('<fetch_tasks ')
        tasks, count = TaskModel.fetch_tasks(*search_args)  # pylint: disable=unused-variable
        tasks_response = []

        for task in tasks:
            tasks_response.append(task)

        current_app.logger.debug('>fetch_tasks ')
        return tasks_response

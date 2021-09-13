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
import urllib
from datetime import datetime
from typing import Dict

from flask import current_app
from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.exceptions import BusinessException, Error
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Org as OrgModel
from auth_api.models import Task as TaskModel
from auth_api.models import User as UserModel
from auth_api.models import db
from auth_api.schemas import TaskSchema
from auth_api.utils.account_mailer import publish_to_mailer
from auth_api.utils.enums import AccessType, OrgStatus, TaskRelationshipStatus, TaskRelationshipType, TaskStatus
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
    def create_task(task_info: dict, do_commit: bool = True):
        """Create a new task record."""
        current_app.logger.debug('<create_task ')
        task_model = TaskModel(**camelback2snake(task_info))
        task_model.flush()
        if do_commit:  # Task mostly comes as a part of parent transaction.So do not commit unless asked.
            db.session.commit()

        current_app.logger.debug('>create_task ')
        return Task(task_model)

    @staticmethod
    def close_task(task_id, remarks: [] = None, do_commit: bool = True):
        """Close a task."""
        current_app.logger.debug('<close_task ')
        task_model: TaskModel = TaskModel.find_by_id(task_id)
        task_model.status = TaskStatus.CLOSED.value
        task_model.remarks = remarks
        task_model.flush()
        if do_commit:
            db.session.commit()

    def update_task(self, task_info: Dict = None, origin_url: str = None):
        """Update a task record."""
        current_app.logger.debug('<update_task ')
        task_model: TaskModel = self._model
        task_relationship_status = task_info.get('relationshipStatus')

        user: UserModel = UserModel.find_by_jwt_token()
        task_model.status = task_info.get('status', TaskStatus.COMPLETED.value)
        task_model.remarks = task_info.get('remarks', None)
        task_model.decision_made_by = user.username
        task_model.decision_made_on = datetime.now()
        task_model.relationship_status = task_relationship_status
        task_model.flush()

        # Update its relationship

        self._update_relationship(origin_url=origin_url)
        current_app.logger.debug('>update_task ')
        db.session.commit()
        return Task(task_model)

    def _update_relationship(self, origin_url: str = None):
        """Retrieve the relationship record and update the status."""
        task_model: TaskModel = self._model
        current_app.logger.debug('<update_task_relationship ')
        is_approved: bool = task_model.relationship_status == TaskRelationshipStatus.ACTIVE.value
        is_hold: bool = task_model.status == TaskStatus.HOLD.value

        if task_model.relationship_type == TaskRelationshipType.ORG.value:
            # Update Org relationship
            org_id = task_model.relationship_id
            if not is_hold:
                self._update_org(is_approved=is_approved, org_id=org_id,
                                 origin_url=origin_url)
            else:
                # no updates on org yet.put the task on hold and send mail to user
                org: OrgModel = OrgModel.find_by_org_id(org_id)
                if org.status_code != OrgStatus.PENDING_STAFF_REVIEW.value:
                    org.status_code = OrgStatus.PENDING_STAFF_REVIEW.value
                    org.flush()
                is_bceid = org.access_type in (AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value)
                # bceid holds need notifications
                if is_bceid:
                    Task._notify_admin_about_hold(org, task_model)

        elif task_model.relationship_type == TaskRelationshipType.PRODUCT.value:
            # Update Product relationship
            product_subscription_id = task_model.relationship_id
            account_id = task_model.account_id
            self._update_product_subscription(is_approved=is_approved, product_subscription_id=product_subscription_id,
                                              org_id=account_id)

        current_app.logger.debug('>update_task_relationship ')

    @staticmethod
    def _notify_admin_about_hold(org, task_model):
        admin_email = ContactLinkModel.find_by_user_id(org.members[0].user.id).contact.email
        create_account_signin_route = urllib.parse.quote_plus(f"{current_app.config.get('BCEID_ACCOUNT_SETUP_ROUTE')}/"
                                                              f'{org.id}')
        data = {
            'remark': task_model.remarks,
            'applicationDate': f"{task_model.created.strftime('%m/%d/%Y')}",
            'accountId': task_model.relationship_id,
            'emailAddresses': admin_email,
            'contextUrl': f"{current_app.config.get('WEB_APP_URL')}"
                          f"/{current_app.config.get('BCEID_SIGNIN_ROUTE')}/"
                          f'{create_account_signin_route}'
        }
        try:
            publish_to_mailer('resubmitBceidOrg', org_id=org.id, data=data)
            current_app.logger.debug('<send_approval_notification_to_member')
        except Exception as e:  # noqa=B901
            current_app.logger.error('<send_notification_to_member failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None) from e

    @staticmethod
    def _update_org(is_approved: bool, org_id: int, origin_url: str = None):
        """Approve/Reject Affidavit and Org."""
        from auth_api.services import Org as OrgService  # pylint:disable=cyclic-import, import-outside-toplevel
        current_app.logger.debug('<update_task_org ')

        OrgService.approve_or_reject(org_id=org_id, is_approved=is_approved,
                                     origin_url=origin_url)

        current_app.logger.debug('>update_task_org ')

    @staticmethod
    def _update_product_subscription(is_approved: bool, product_subscription_id: int, org_id: int):
        """Review Product Subscription."""
        current_app.logger.debug('<_update_product_subscription ')
        from auth_api.services import Product as ProductService  # pylint:disable=cyclic-import, import-outside-toplevel

        # Approve/Reject Product subscription
        ProductService.update_product_subscription(product_subscription_id=product_subscription_id,
                                                   is_approved=is_approved, org_id=org_id, is_new_transaction=False)
        current_app.logger.debug('>_update_product_subscription ')

    @staticmethod
    def fetch_tasks(**kwargs):
        """Search all tasks."""
        task_type = kwargs.get('task_type')
        task_status = kwargs.get('task_status') or [TaskStatus.OPEN.value]
        task_relationship_status = kwargs.get('task_relationship_status')

        tasks = {'tasks': []}
        page: int = int(kwargs.get('page'))
        limit: int = int(kwargs.get('limit'))
        search_args = (task_type,
                       task_status,
                       task_relationship_status,
                       page,
                       limit)

        current_app.logger.debug('<fetch_tasks ')
        task_models, count = TaskModel.fetch_tasks(*search_args)  # pylint: disable=unused-variable

        if not task_models:
            return tasks

        for task in task_models:
            task_dict = Task(task).as_dict()
            tasks['tasks'].append(task_dict)

        tasks['total'] = count
        tasks['page'] = page
        tasks['limit'] = limit

        current_app.logger.debug('>fetch_tasks ')
        return tasks

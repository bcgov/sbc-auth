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
from typing import Dict, List

from flask import current_app
from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.exceptions import BusinessException, Error
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import Task as TaskModel
from auth_api.models import User as UserModel
from auth_api.models import db
from auth_api.schemas import TaskSchema
from auth_api.services.user import User as UserService
from auth_api.utils.account_mailer import publish_to_mailer
from auth_api.utils.enums import Status, TaskRelationshipStatus, TaskRelationshipType, TaskStatus, TaskAction
from auth_api.utils.util import camelback2snake  # noqa: I005
from auth_api.models.dataclass import TaskSearch

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
    def as_dict(self, exclude: List = None):
        """Return the Task as a python dict.

        None fields are not included in the dict.
        """
        exclude = exclude or []
        task_schema = TaskSchema(exclude=exclude)
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

        self._update_relationship(origin_url=origin_url)
        db.session.commit()
        current_app.logger.debug('>update_task ')
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
                                 origin_url=origin_url, task_action=task_model.action)
            else:
                # Task with ACCOUNT_REVIEW action cannot be put on hold
                if task_model.action != TaskAction.AFFIDAVIT_REVIEW.value:
                    raise BusinessException(Error.INVALID_INPUT, None)

                # no updates on org yet.put the task on hold and send mail to user
                org: OrgModel = OrgModel.find_by_org_id(org_id)
                # send on-hold mail notification
                Task._notify_admin_about_hold(task_model, org=org)
            # TODO Update user.verified flag
        elif task_model.relationship_type == TaskRelationshipType.PRODUCT.value:
            # Update Product relationship
            product_subscription_id = task_model.relationship_id
            account_id = task_model.account_id
            self._update_product_subscription(is_approved=is_approved, product_subscription_id=product_subscription_id,
                                              org_id=account_id)

        elif task_model.relationship_type == TaskRelationshipType.USER.value:
            user_id = task_model.relationship_id
            if not is_hold:
                self._update_bceid_admin(is_approved=is_approved, user_id=user_id)
            else:
                user: UserModel = UserModel.find_by_id(user_id)
                membership = MembershipModel.find_membership_by_userid(user_id)
                # Send mail to admin about hold with reasons
                Task._notify_admin_about_hold(user=user, task_model=task_model, is_new_bceid_admin_request=True,
                                              membership_id=membership.id)

        # If action is affidavit review, mark the user as verified.
        if is_approved and task_model.action == TaskAction.AFFIDAVIT_REVIEW.value and task_model.user:
            task_model.user.verified = True
            task_model.user.save()

        current_app.logger.debug('>update_task_relationship ')

    @staticmethod
    def _notify_admin_about_hold(task_model, org: OrgModel = None, is_new_bceid_admin_request: bool = False,
                                 membership_id: int = None, user: UserModel = None):
        if is_new_bceid_admin_request:
            create_account_signin_route = urllib.parse.quote_plus(
                f"{current_app.config.get('BCEID_ADMIN_SETUP_ROUTE')}/"
                f'{task_model.account_id}/'
                f'{membership_id}')
            admin_emails = user.contacts[0].contact.email if user.contacts else ''
            account_id = task_model.account_id
            mailer_type = 'resubmitBceidAdmin'

        else:
            create_account_signin_route = urllib.parse. \
                quote_plus(f"{current_app.config.get('BCEID_ACCOUNT_SETUP_ROUTE')}/"
                           f'{org.id}')
            admin_emails = UserService.get_admin_emails_for_org(org.id)
            account_id = org.id
            mailer_type = 'resubmitBceidOrg'

        if admin_emails == '':
            current_app.logger.error('No admin email record for org id {}', org.id)
            current_app.logger.error('<send_approval_notification_to_member failed')
            return

        data = {
            'remarks': task_model.remarks,
            'applicationDate': f"{task_model.created.strftime('%m/%d/%Y')}",
            'accountId': account_id,
            'emailAddresses': admin_emails,
            'contextUrl': f"{current_app.config.get('WEB_APP_URL')}"
            f"/{current_app.config.get('BCEID_SIGNIN_ROUTE')}/"
            f'{create_account_signin_route}'
        }
        try:
            publish_to_mailer(mailer_type, org_id=account_id, data=data)
            current_app.logger.debug('<send_approval_notification_to_member')
        except Exception as e:  # noqa=B901
            current_app.logger.error('<send_notification_to_member failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None) from e

    @staticmethod
    def _update_org(is_approved: bool, org_id: int, origin_url: str = None, task_action: str = None):
        """Approve/Reject Affidavit and Org."""
        from auth_api.services import Org as OrgService  # pylint:disable=cyclic-import, import-outside-toplevel
        current_app.logger.debug('<update_task_org ')

        OrgService.approve_or_reject(org_id=org_id, is_approved=is_approved,
                                     origin_url=origin_url, task_action=task_action)

        current_app.logger.debug('>update_task_org ')

    @staticmethod
    def _update_bceid_admin(is_approved: bool, user_id: int):
        """Approve/Reject BCeId Admin User and Affidavit."""
        from auth_api.services import Affidavit  # pylint:disable=cyclic-import, import-outside-toplevel
        current_app.logger.debug('<update_bceid_admin_to_org ')

        # Update user
        user: UserModel = UserModel.find_by_id(user_id)
        user.status = Status.ACTIVE.value if is_approved else Status.INACTIVE.value

        # Update membership
        membership = MembershipModel.find_membership_by_userid(user_id)
        membership.status = Status.ACTIVE.value if is_approved else Status.REJECTED.value

        # Update affidavit
        Affidavit.approve_or_reject_bceid_admin(admin_user_id=user_id, is_approved=is_approved, user=user)

        current_app.logger.debug('>update_bceid_admin_to_org ')

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
    def fetch_tasks(task_search: TaskSearch):
        """Search all tasks."""
        current_app.logger.debug('<fetch_tasks ')
        task_models, count = TaskModel.fetch_tasks(task_search)  # pylint: disable=unused-variable

        tasks = {
            'tasks': [Task(task).as_dict(exclude=['user']) for task in task_models],
            'total': count,
            'page': task_search.page,
            'limit': task_search.limit
        }

        current_app.logger.debug('>fetch_tasks ')
        return tasks

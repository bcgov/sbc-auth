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
"""The User service.

This module manages the User Information.
"""
from datetime import datetime
from typing import Dict

from flask import current_app
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import Task as TaskModel
from auth_api.models.affidavit import Affidavit as AffidavitModel
from auth_api.models.user import User as UserModel
from auth_api.schemas import AffidavitSchema
from auth_api.services.minio import MinioService
from auth_api.services.task import Task as TaskService
from auth_api.utils.enums import (
    AffidavitStatus, TaskRelationshipStatus, TaskRelationshipType, TaskStatus, TaskTypePrefix)
from auth_api.utils.util import camelback2snake

from .user import User as UserService


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Affidavit:  # pylint: disable=too-many-instance-attributes
    """Manages all aspects of the Affidavit Entity."""

    def __init__(self, model):
        """Return a affidavit object."""
        self._model = model

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the Affidavit as a python dict.

        None fields are not included in the dict.
        """
        affidavit_schema = AffidavitSchema()
        obj = affidavit_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    def create_affidavit(affidavit_info: Dict):
        """Create a new affidavit record."""
        current_app.logger.debug('<create_affidavit ')
        user = UserService.find_by_jwt_token()
        # If the user already have a pending affidavit, raise error
        existing_affidavit: AffidavitModel = AffidavitModel.find_pending_by_user_id(user_id=user.identifier)
        trigger_task_update = False
        if existing_affidavit is not None:
            # inactivate the current affidavit
            existing_affidavit.status_code = AffidavitStatus.INACTIVE.value
            existing_affidavit.flush()
            trigger_task_update = True

        contact = affidavit_info.pop('contact')
        affidavit_model = AffidavitModel(
            issuer=affidavit_info.get('issuer'),
            document_id=affidavit_info.get('documentId'),
            status_code=AffidavitStatus.PENDING.value,
            user_id=user.identifier
        )
        affidavit_model.add_to_session()

        # Save contact for the affidavit
        if contact:
            contact = ContactModel(**camelback2snake(contact))
            contact.add_to_session()

            contact_link = ContactLinkModel()
            contact_link.affidavit = affidavit_model
            contact_link.contact = contact
            contact_link.add_to_session()

        affidavit_model.save()

        if trigger_task_update:
            Affidavit._modify_task(user)

        return Affidavit(affidavit_model)

    @staticmethod
    def _modify_task(user):
        # find users org. ideally only one org
        org_list = MembershipModel.find_orgs_for_user(user.identifier)
        org: OrgModel = next(iter(org_list or []), None)
        if org:
            # check if there is any holding tasks
            task_model: TaskModel = TaskModel.find_by_task_for_account(org.id, TaskStatus.HOLD.value)
            if task_model:
                task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
                task_info = {'name': org.name,
                             'relationshipId': org.id,
                             'relatedTo': user.identifier,
                             'dateSubmitted': task_model.date_submitted,
                             'relationshipType': TaskRelationshipType.ORG.value,
                             'type': task_type,
                             'status': TaskStatus.OPEN.value,
                             'relationship_status': TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
                             }
                new_task = TaskService.create_task(task_info=task_info, do_commit=False)

                # Send notification mail to staff review task
                from auth_api.services import Org as OrgService  # pylint:disable=cyclic-import, import-outside-toplevel
                OrgService.send_staff_review_account_reminder(relationship_id=org.id)

                remarks = [f'User Uploaded New affidavit .Created New task id: {new_task.identifier}']
                TaskService.close_task(task_model.id, remarks)

    @staticmethod
    def find_affidavit_by_org_id(org_id: int):
        """Return affidavit for the org by finding the admin for the org."""
        current_app.logger.debug('<find_affidavit_by_org_id ')
        affidavit = AffidavitModel.find_by_org_id(org_id)
        affidavit_dict = Affidavit(affidavit).as_dict()
        affidavit_dict['documentUrl'] = MinioService.create_signed_get_url(affidavit.document_id)
        current_app.logger.debug('>find_affidavit_by_org_id ')
        return affidavit_dict

    @staticmethod
    def approve_or_reject(org_id: int, is_approved: bool, user: UserModel):
        """Mark the affdiavit as approved or rejected."""
        current_app.logger.debug('<find_affidavit_by_org_id ')
        affidavit: AffidavitModel = AffidavitModel.find_by_org_id(org_id)
        affidavit.decision_made_by = user.username
        affidavit.decision_made_on = datetime.now()
        affidavit.status_code = AffidavitStatus.APPROVED.value if is_approved else AffidavitStatus.REJECTED.value

        current_app.logger.debug('>find_affidavit_by_org_id ')
        return Affidavit(affidavit)

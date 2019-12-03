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
"""The Membership service.

This module manages the Membership Information between an org and a user.
"""
from typing import Dict, Tuple

from flask import current_app
from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Membership as MembershipModel
from auth_api.models import MembershipStatusCode as MembershipStatusCodeModel
from auth_api.models import MembershipType as MembershipTypeModel
from auth_api.models import Org as OrgModel
from auth_api.schemas import MembershipSchema
from auth_api.utils.roles import ADMIN, ALL_ALLOWED_ROLES, OWNER, Status
from config import get_named_config

from .authorization import check_auth
from .notification import send_email

ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)
CONFIG = get_named_config()


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Membership:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Manages all aspects of the Membership Entity.

    This manages storing the Membership in the cache,
    ensuring that the local cache is up to date,
    submitting changes back to all storage systems as needed.
    """

    def __init__(self, model):
        """Return a membership service object."""
        self._model = model

    def as_dict(self):
        """Return the Membership as a python dict.

        None fields are not included in the dict.
        """
        membership_schema = MembershipSchema()
        obj = membership_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    def get_membership_type_by_code(type_code):
        """Get a membership type by the given code."""
        return MembershipTypeModel.get_membership_type_by_code(type_code=type_code)

    @staticmethod
    def get_members_for_org(org_id, status=None, membership_roles=None, token_info: Dict = None,
                            allowed_roles: Tuple = None):
        """Get members of org.Fetches using status and roles."""
        if org_id is None:
            return None

        if membership_roles is None:
            membership_roles = ALL_ALLOWED_ROLES
        if not status:
            status = Status.ACTIVE.value
        else:
            status = Status[status].value

        org_model = OrgModel.find_by_org_id(org_id)
        if not org_model:
            return None

        # Check authorization for the user
        check_auth(token_info, one_of_roles=allowed_roles, org_id=org_id)
        return MembershipModel.find_members_by_org_id_by_status_by_roles(org_id, membership_roles, status)

    @staticmethod
    def get_membership_status_by_code(name):
        """Get a membership type by the given code."""
        return MembershipStatusCodeModel.get_membership_status_by_code(name=name)

    @classmethod
    def find_membership_by_id(cls, membership_id, token_info: Dict = None):
        """Retrieve a membership record by id."""
        membership = MembershipModel.find_membership_by_id(membership_id)

        if membership:
            # Ensure that this user is an ADMIN or OWNER on the org associated with this membership
            # or that the membership is for the current user
            if membership.user.username != token_info.get('username'):
                check_auth(org_id=membership.org_id, token_info=token_info, one_of_roles=(ADMIN, OWNER))
            return Membership(membership)
        return None

    def send_approval_notification_to_member(self, origin_url):
        """Send the admin email notification."""
        current_app.logger.debug('<send_approval_notification_to_member')
        org_name = self._model.org.name
        subject = '[BC Registries & Online Services] Welcome to the team {}'. \
            format(org_name)
        sender = CONFIG.MAIL_FROM_ID
        template = ENV.get_template('email_templates/membership_approved_notification_email.html')
        context_path = CONFIG.AUTH_WEB_TOKEN_CONFIRM_PATH
        app_url = '{}/{}'.format(origin_url, context_path)

        sent_response = send_email(subject, sender, self._model.user.contacts[0].contact.email,
                                   template.render(url=app_url, org_name=org_name,
                                                   logo_url=f'{app_url}/{CONFIG.REGISTRIES_LOGO_IMAGE_NAME}'))
        current_app.logger.debug('<send_approval_notification_to_member')
        if not sent_response:
            # invitation.invitation_status_code = 'FAILED'
            # invitation.save()
            current_app.logger.error('<send_approval_notification_to_member failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None)

    def update_membership(self, updated_fields, token_info: Dict = None):
        """Update an existing membership with the given role."""
        # Ensure that this user is an ADMIN or OWNER on the org associated with this membership
        current_app.logger.debug('<update_membership')
        check_auth(org_id=self._model.org_id, token_info=token_info, one_of_roles=(ADMIN, OWNER))
        for key, value in updated_fields.items():
            if value is not None:
                setattr(self._model, key, value)
        self._model.save()
        self._model.commit()
        current_app.logger.debug('>update_membership')
        return self

    def deactivate_membership(self, token_info: Dict = None):
        """Mark this membership as inactive."""
        current_app.logger.debug('<deactivate_membership')
        if self._model.user.username != token_info.get('username'):
            check_auth(token_info=token_info, one_of_roles=(ADMIN, OWNER))
        self._model.membership_status = MembershipStatusCodeModel.get_membership_status_by_code('INACTIVE')
        current_app.logger.info(f'<deactivate_membership for {self._model.user.username}')
        self._model.save()
        self._model.commit()
        current_app.logger.debug('>deactivate_membership')
        return self

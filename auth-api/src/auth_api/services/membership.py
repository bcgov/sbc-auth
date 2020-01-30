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
from typing import Dict

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
from auth_api.utils.enums import NotificationType
from auth_api.utils.roles import ADMIN, ALL_ALLOWED_ROLES, OWNER, Status
from config import get_named_config

from .authorization import check_auth
from .notification import send_email
from .org import Org as OrgService
from .user import User as UserService


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
    def get_members_for_org(org_id, status=Status.ACTIVE,  # pylint:disable=too-many-return-statements
                            membership_roles=ALL_ALLOWED_ROLES,
                            token_info: Dict = None):
        """Get members of org.Fetches using status and roles."""
        org_model = OrgModel.find_by_org_id(org_id)
        if not org_model:
            return None

        status = Status.ACTIVE.value if status is None else Status[status].value
        membership_roles = ALL_ALLOWED_ROLES if membership_roles is None else membership_roles

        # If staff return full list
        if 'staff' in token_info.get('realm_access').get('roles'):
            return MembershipModel.find_members_by_org_id_by_status_by_roles(org_id, membership_roles, status)

        current_user: UserService = UserService.find_by_jwt_token(token_info)
        current_user_membership: MembershipModel = \
            MembershipModel.find_membership_by_user_and_org(user_id=current_user.identifier, org_id=org_id)

        # If no active or pending membership return empty array
        if current_user_membership is None or \
                current_user_membership.status == Status.INACTIVE.value or \
                current_user_membership.status == Status.REJECTED.value:
            return []

        # If pending approval, return empty for active, array of self only for pending
        if current_user_membership.status == Status.PENDING_APPROVAL.value:
            return [current_user_membership] if status == Status.PENDING_APPROVAL.value else []

        # If active status for current user, then check organizational role
        if current_user_membership.status == Status.ACTIVE.value:
            if current_user_membership.membership_type_code == OWNER or \
                    current_user_membership.membership_type_code == ADMIN:
                return MembershipModel.find_members_by_org_id_by_status_by_roles(org_id, membership_roles, status)

            return MembershipModel.find_members_by_org_id_by_status_by_roles(org_id, membership_roles, status) \
                if status == Status.ACTIVE.value else []

        return []

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

    def send_notification_to_member(self, origin_url, notification_type):
        """Send member notification."""
        current_app.logger.debug(f'<send {notification_type} notification')
        org_name = self._model.org.name
        template_name = ''
        params = {}
        if notification_type == NotificationType.ROLE_CHANGED.value:
            subject = '[BC Registries & Online Services] Your Role has been changed'
            template_name = 'role_changed_notification_email.html'
            params = {'org_name': org_name, 'role': self._model.membership_type.code,
                      'label': self._model.membership_type.label}
        elif notification_type == NotificationType.MEMBERSHIP_APPROVED.value:
            subject = '[BC Registries & Online Services] Welcome to the account {}'. \
                format(org_name)
            template_name = 'membership_approved_notification_email.html'
            params = {'org_name': org_name}
        sender = CONFIG.MAIL_FROM_ID
        template = ENV.get_template(f'email_templates/{template_name}')
        context_path = CONFIG.AUTH_WEB_TOKEN_CONFIRM_PATH
        app_url = '{}/{}'.format(origin_url, context_path)

        try:
            sent_response = send_email(subject, sender, self._model.user.contacts[0].contact.email,
                                       template.render(url=app_url, params=params,
                                                       logo_url=f'{app_url}/{CONFIG.REGISTRIES_LOGO_IMAGE_NAME}'))
            current_app.logger.debug('<send_approval_notification_to_member')
            if not sent_response:
                current_app.logger.error('<send_notification_to_member failed')
                raise BusinessException(Error.FAILED_NOTIFICATION, None)
        except:  # noqa=B901
            current_app.logger.error('<send_notification_to_member failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None)

    def update_membership(self, updated_fields, token_info: Dict = None):
        """Update an existing membership with the given role."""
        # Ensure that this user is an ADMIN or OWNER on the org associated with this membership
        current_app.logger.debug('<update_membership')
        check_auth(org_id=self._model.org_id, token_info=token_info, one_of_roles=(ADMIN, OWNER))

        # Ensure that a member does not upgrade a member to OWNER from ADMIN unless they are an OWNER themselves
        if self._model.membership_type.code == ADMIN and updated_fields.get('membership_type', None) == OWNER:
            check_auth(org_id=self._model.org_id, token_info=token_info, one_of_roles=(OWNER))

        # No one can change an OWNER's status, only option is OWNER to leave the team. #2319
        if updated_fields.get('membership_status', None) \
                and updated_fields['membership_status'].id == Status.INACTIVE.value \
                and self._model.membership_type.code == OWNER:
            raise BusinessException(Error.OWNER_CANNOT_BE_REMOVED, None)

        # Ensure that if downgrading from owner that there is at least one other owner in org
        if self._model.membership_type.code == OWNER and \
                updated_fields.get('membership_type', None) != OWNER and \
                OrgService(self._model.org).get_owner_count() == 1:
            raise BusinessException(Error.CHANGE_ROLE_FAILED_ONLY_OWNER, None)

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
        # if this is a member removing another member, check that they admin or owner
        if self._model.user.username != token_info.get('username'):
            check_auth(org_id=self._model.org_id, token_info=token_info, one_of_roles=(ADMIN, OWNER))

        # check to ensure that owner isn't removed by anyone but an owner
        if self._model.membership_type == OWNER:
            check_auth(org_id=self._model.org_id, token_info=token_info, one_of_roles=(OWNER))

        self._model.membership_status = MembershipStatusCodeModel.get_membership_status_by_code('INACTIVE')
        current_app.logger.info(f'<deactivate_membership for {self._model.user.username}')
        self._model.save()
        self._model.commit()
        current_app.logger.debug('>deactivate_membership')
        return self

    @staticmethod
    def get_membership_for_org_and_user(org_id, user_id):
        """Get the membership for the given org and user id."""
        return MembershipModel.find_membership_by_user_and_org(user_id, org_id)

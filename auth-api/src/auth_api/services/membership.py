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

import json
from flask import current_app
from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.config import get_named_config
from auth_api.models.dataclass import Activity
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import MembershipStatusCode as MembershipStatusCodeModel
from auth_api.models import MembershipType as MembershipTypeModel
from auth_api.models import Org as OrgModel
from auth_api.schemas import MembershipSchema
from auth_api.utils.enums import ActivityAction, LoginSource, NotificationType, Status
from auth_api.utils.roles import ADMIN, ALL_ALLOWED_ROLES, COORDINATOR, STAFF
from auth_api.utils.user_context import UserContext, user_context
from .activity_log_publisher import ActivityLogPublisher
from .authorization import check_auth
from .keycloak import KeycloakService
from .org import Org as OrgService
from .user import User as UserService
from ..utils.account_mailer import publish_to_mailer

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
    def get_pending_member_count_for_org(org_id):
        """Return the number of pending notification for a user."""
        default_count = 0
        try:
            current_user: UserService = UserService.find_by_jwt_token()
        except BusinessException:
            return default_count
        is_active_admin_or_owner = MembershipModel.check_if_active_admin_or_owner_org_id(org_id,
                                                                                         current_user.identifier)
        if is_active_admin_or_owner < 1:
            return default_count
        pending_member_count = MembershipModel.get_pending_members_count_by_org_id(org_id)
        return pending_member_count

    @staticmethod
    @user_context
    def get_members_for_org(org_id, status=Status.ACTIVE.name,  # pylint:disable=too-many-return-statements
                            membership_roles=ALL_ALLOWED_ROLES, **kwargs):
        """Get members of org.Fetches using status and roles."""
        org_model = OrgModel.find_by_org_id(org_id)
        if not org_model:
            return None

        user_from_context: UserContext = kwargs['user_context']
        status = Status.ACTIVE.value if status is None else Status[status].value
        membership_roles = ALL_ALLOWED_ROLES if membership_roles is None else membership_roles
        # If staff return full list
        if user_from_context.is_staff():
            return MembershipModel.find_members_by_org_id_by_status_by_roles(org_id, membership_roles, status)

        current_user: UserService = UserService.find_by_jwt_token()
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
            if current_user_membership.membership_type_code in (ADMIN, COORDINATOR):
                return MembershipModel.find_members_by_org_id_by_status_by_roles(org_id, membership_roles, status)

            return MembershipModel.find_members_by_org_id_by_status_by_roles(org_id, membership_roles, status) \
                if status == Status.ACTIVE.value else []

        return []

    @staticmethod
    def get_membership_status_by_code(name):
        """Get a membership type by the given code."""
        return MembershipStatusCodeModel.get_membership_status_by_code(name=name)

    @classmethod
    @user_context
    def find_membership_by_id(cls, membership_id, **kwargs):
        """Retrieve a membership record by id."""
        user_from_context: UserContext = kwargs['user_context']
        membership = MembershipModel.find_membership_by_id(membership_id)

        if membership:
            # Ensure that this user is an COORDINATOR or ADMIN on the org associated with this membership
            # or that the membership is for the current user
            if membership.user.username != user_from_context.user_name:
                check_auth(org_id=membership.org_id, one_of_roles=(COORDINATOR, ADMIN, STAFF))
            return Membership(membership)
        return None

    def send_notification_to_member(self, origin_url, notification_type):
        """Send member notification."""
        current_app.logger.debug(f'<send {notification_type} notification')
        org_name = self._model.org.name
        org_id = self._model.org.id
        if not self._model.user.contacts:
            current_app.logger.error('No user contact record for user id {}', self._model.user_id)
            current_app.logger.error('<send_notification_to_member failed')
        recipient = self._model.user.contacts[0].contact.email
        context_path = CONFIG.AUTH_WEB_TOKEN_CONFIRM_PATH
        app_url = f'{origin_url}/{context_path}'
        notification_type_for_mailer = ''
        data = {}
        if notification_type == NotificationType.ROLE_CHANGED.value:
            notification_type_for_mailer = 'roleChangedNotification'
            data = {
                'accountId': org_id,
                'emailAddresses': recipient,
                'contextUrl': app_url,
                'orgName': org_name,
                'role': self._model.membership_type.code,
                'label': self._model.membership_type.label
            }
        elif notification_type == NotificationType.MEMBERSHIP_APPROVED.value:
            # TODO how to check properly if user is bceid user
            is_bceid_user = self._model.user.username.find('@bceid') > 0
            if is_bceid_user:
                notification_type_for_mailer = 'membershipApprovedNotificationForBceid'
            else:
                notification_type_for_mailer = 'membershipApprovedNotification'

            data = {
                'accountId': org_id,
                'emailAddresses': recipient,
                'contextUrl': app_url,
                'orgName': org_name
            }

        try:
            publish_to_mailer(notification_type_for_mailer, org_id=org_id, data=data)
            current_app.logger.debug('<send_approval_notification_to_member')
        except Exception as e:  # noqa=B901
            current_app.logger.error('<send_notification_to_member failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None) from e

    @user_context
    def update_membership(self, updated_fields, **kwargs):
        """Update an existing membership with the given role."""
        # Ensure that this user is an COORDINATOR or ADMIN on the org associated with this membership
        current_app.logger.debug('<update_membership')
        user_from_context: UserContext = kwargs['user_context']
        check_auth(org_id=self._model.org_id, one_of_roles=(COORDINATOR, ADMIN, STAFF))

        # bceid Members cant be ADMIN's.Unless they have an affidavit approved.
        # TODO when multiple teams for bceid are present , do if the user has affidavit present check
        is_bceid_user = self._model.user.login_source == LoginSource.BCEID.value
        if is_bceid_user and getattr(updated_fields.get('membership_type', None), 'code', None) == ADMIN:
            raise BusinessException(Error.BCEID_USERS_CANT_BE_OWNERS, None)

        # Ensure that a member does not upgrade a member to ADMIN from COORDINATOR unless they are an ADMIN themselves
        if self._model.membership_type.code == COORDINATOR and updated_fields.get('membership_type', None) == ADMIN:
            check_auth(org_id=self._model.org_id, one_of_roles=(ADMIN, STAFF))

        updated_membership_status = updated_fields.get('membership_status')
        admin_getting_removed: bool = False
        # Admin can be removed by other admin or staff. #4909
        if updated_membership_status \
                and updated_membership_status.id == Status.INACTIVE.value \
                and self._model.membership_type.code == ADMIN:
            admin_getting_removed = True
            if OrgService(self._model.org).get_owner_count() == 1:
                raise BusinessException(Error.CHANGE_ROLE_FAILED_ONLY_OWNER, None)

        # Ensure that if downgrading from owner that there is at least one other owner in org
        if self._model.membership_type.code == ADMIN and \
                updated_fields.get('membership_type', None) != ADMIN and \
                OrgService(self._model.org).get_owner_count() == 1:
            raise BusinessException(Error.CHANGE_ROLE_FAILED_ONLY_OWNER, None)

        for key, value in updated_fields.items():
            if value is not None:
                setattr(self._model, key, value)
        self._model.save()

        membership_type = updated_fields.get('membership_type') or self._model.membership_type.code
        if updated_membership_status \
                and updated_membership_status.id in [Status.INACTIVE.value, Status.ACTIVE.value]:
            action = ActivityAction.APPROVE_TEAM_MEMBER.value \
                if updated_membership_status.id == Status.ACTIVE.value  \
                else ActivityAction.REMOVE_TEAM_MEMBER.value
            name = {'first_name': self._model.user.firstname, 'last_name': self._model.user.lastname}
            ActivityLogPublisher.publish_activity(Activity(self._model.org_id, action,
                                                           name=json.dumps(name), id=self._model.user.id,
                                                           value=membership_type))
        # Add to account_holders group in keycloak
        Membership._add_or_remove_group(self._model)
        is_bcros_user = self._model.user.login_source == LoginSource.BCROS.value
        # send mail if staff modifies , not applicable for bcros , only if anything is getting updated
        if user_from_context.is_staff() and not is_bcros_user and len(updated_fields) != 0:
            publish_to_mailer(notification_type='teamModified', org_id=self._model.org.id)

        # send mail to the person itself who is getting removed by staff ;if he is admin and has an email on record
        if user_from_context.is_staff() and not is_bcros_user and admin_getting_removed:
            contact_link = ContactLinkModel.find_by_user_id(self._model.user.id)
            if contact_link and contact_link.contact.email:
                data = {
                    'accountId': self._model.org.id,
                    'recipientEmail': contact_link.contact.email
                }
                publish_to_mailer(notification_type='adminRemoved', org_id=self._model.org.id, data=data)

        current_app.logger.debug('>update_membership')
        return self

    @user_context
    def deactivate_membership(self, **kwargs):
        """Mark this membership as inactive."""
        current_app.logger.debug('<deactivate_membership')
        user_from_context: UserContext = kwargs['user_context']
        # if this is a member removing another member, check that they admin or owner
        if self._model.user.username != user_from_context.user_name:
            check_auth(org_id=self._model.org_id, one_of_roles=(COORDINATOR, ADMIN))

        # check to ensure that owner isn't removed by anyone but an owner
        if self._model.membership_type == ADMIN:
            check_auth(org_id=self._model.org_id, one_of_roles=(ADMIN))

        self._model.membership_status = MembershipStatusCodeModel.get_membership_status_by_code('INACTIVE')
        current_app.logger.info(f'<deactivate_membership for {self._model.user.username}')
        self._model.save()
        # Remove from account_holders group in keycloak
        Membership._add_or_remove_group(self._model)
        name = {'first_name': self._model.user.firstname, 'last_name': self._model.user.lastname}
        ActivityLogPublisher.publish_activity(Activity(self._model.org_id,
                                                       ActivityAction.REMOVE_TEAM_MEMBER.value,
                                                       name=json.dumps(name),
                                                       id=self._model.user.id))
        current_app.logger.debug('>deactivate_membership')
        return self

    @staticmethod
    def _add_or_remove_group(model: MembershipModel):
        """Add or remove the user from/to account holders group."""
        if model.membership_status.id == Status.ACTIVE.value:
            KeycloakService.join_account_holders_group(model.user.keycloak_guid)
        elif model.membership_status.id == Status.INACTIVE.value and len(
                MembershipModel.find_orgs_for_user(model.user.id)) == 0:
            # Check if the user has any other active org membership, if none remove from the group
            KeycloakService.remove_from_account_holders_group(model.user.keycloak_guid)

    @staticmethod
    def get_membership_for_org_and_user(org_id, user_id):
        """Get the membership for the given org and user id."""
        return MembershipModel.find_membership_by_user_and_org(user_id, org_id)

    @staticmethod
    def get_membership_for_org_and_user_all_status(org_id, user_id):
        """Get the membership for the specified user and org with all memebership statuses."""
        return MembershipModel.find_membership_by_user_and_org_all_status(user_id, org_id)

    @staticmethod
    def add_staff_membership(user_id):
        """Add a staff membership for the specified user."""
        if MembershipModel.find_active_staff_org_memberships_for_user(user_id):
            return
        MembershipModel.add_membership_for_staff(user_id)

    @staticmethod
    def remove_staff_membership(user_id):
        """Remove staff membership for the specified user."""
        MembershipModel.remove_membership_for_staff(user_id)

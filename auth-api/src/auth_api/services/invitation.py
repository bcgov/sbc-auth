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
"""Service for managing Invitation data."""

from datetime import datetime
from typing import Dict
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Invitation as InvitationModel
from auth_api.models import InvitationStatus as InvitationStatusModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import OrgSettings as OrgSettingsModel
from auth_api.models.org import Org as OrgModel
from auth_api.schemas import InvitationSchema
from auth_api.services.user import User as UserService
from auth_api.utils.roles import ADMIN, OWNER, Status
from config import get_named_config

from .authorization import check_auth
from .notification import send_email


ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)
CONFIG = get_named_config()


class Invitation:
    """Manages Invitation data.

    This service manages creating, updating, and retrieving Invitation data via the Invitation model.
    """

    def __init__(self, model):
        """Return an invitation service instance."""
        self._model = model

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the internal Invitation model as a dictionary."""
        invitation_schema = InvitationSchema()
        obj = invitation_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    def create_invitation(invitation_info: Dict, user, token_info: Dict, invitation_origin):
        """Create a new invitation."""
        # Ensure that the current user is OWNER or ADMIN on each org being invited to
        context_path = CONFIG.AUTH_WEB_TOKEN_CONFIRM_PATH
        for membership in invitation_info['membership']:
            org_id = membership['orgId']
            check_auth(token_info, org_id=org_id, one_of_roles=(OWNER, ADMIN))
        # TODO doesnt work when invited to multiple teams.. Re-work the logic when multiple teams introduced
        org_name = OrgModel.find_by_org_id(invitation_info['membership'][0]['orgId']).name

        invitation = InvitationModel.create_from_dict(invitation_info, user.identifier)
        invitation.save()
        Invitation.send_invitation(invitation, org_name, user.as_dict(),
                                   '{}/{}'.format(invitation_origin, context_path))
        return Invitation(invitation)

    def update_invitation(self, user, token_info: Dict, invitation_origin):
        """Update the specified invitation with new data."""
        # Ensure that the current user is OWNER or ADMIN on each org being re-invited to
        context_path = CONFIG.AUTH_WEB_TOKEN_CONFIRM_PATH
        for membership in self._model.membership:
            org_id = membership.org_id
            check_auth(token_info, org_id=org_id, one_of_roles=(OWNER, ADMIN))

        # TODO doesnt work when invited to multiple teams.. Re-work the logic when multiple teams introduced
        updated_invitation = self._model.update_invitation_as_retried()
        org_name = OrgModel.find_by_org_id(self._model.membership[0].org_id).name
        Invitation.send_invitation(updated_invitation, org_name, user.as_dict(),
                                   '{}/{}'.format(invitation_origin, context_path))
        return Invitation(updated_invitation)

    @staticmethod
    def delete_invitation(invitation_id, token_info: Dict = None):
        """Delete the specified invitation."""
        # Ensure that the current user is OWNER or ADMIN for each org in the invitation
        invitation = InvitationModel.find_invitation_by_id(invitation_id)
        if invitation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        for membership in invitation.membership:
            org_id = membership.org_id
            check_auth(token_info, org_id=org_id, one_of_roles=(OWNER, ADMIN))
        invitation.delete()

    @staticmethod
    def get_invitations_by_org_id(org_id, status, token_info: Dict = None):
        """Get invitations for an org."""
        check_auth(token_info, org_id=org_id, one_of_roles=(OWNER, ADMIN))
        collection = []
        if status == 'ALL':
            invitations = InvitationModel.find_invitations_by_org(org_id)
        else:
            invitations = InvitationModel.find_pending_invitations_by_org(org_id)
        for invitation in invitations:
            collection.append(Invitation(invitation).as_dict())
        return collection

    @staticmethod
    def find_invitation_by_id(invitation_id, token_info: Dict = None):
        """Find an existing invitation with the provided id."""
        if invitation_id is None:
            return None

        invitation = InvitationModel.find_invitation_by_id(invitation_id)
        if not invitation:
            return None

        # Ensure that the current user is an OWNER or ADMIN on each org in the invite being retrieved
        for membership in invitation.membership:
            org_id = membership.org_id
            check_auth(token_info, org_id=org_id, one_of_roles=(OWNER, ADMIN))

        return Invitation(invitation)

    @staticmethod
    def send_admin_notification(user, url, recipient_email_list, org_name):
        """Send the admin email notification."""
        subject = '[BC Registries & Online Services] {} {} has responded for the invitation to join the team {}'. \
            format(user['firstname'], user['firstname'], org_name)
        sender = CONFIG.MAIL_FROM_ID
        try:
            template = ENV.get_template('email_templates/admin_notification_email.html')
        except Exception as err:
            raise BusinessException(Error.FAILED_INVITATION, None)

        sent_response = send_email(subject, sender, recipient_email_list,
                                   template.render(url=url, user=user, org_name=org_name,
                                                   logo_url=f'{url}/{CONFIG.REGISTRIES_LOGO_IMAGE_NAME}'))
        if not sent_response:
            # invitation.invitation_status_code = 'FAILED'
            # invitation.save()
            raise BusinessException(Error.FAILED_INVITATION, None)

    @staticmethod
    def send_invitation(invitation: InvitationModel, org_name, user, app_url):
        """Send the email notification."""
        current_app.logger.debug('<send_invitation')
        subject = '[BC Registries & Online Services] {} {} has invited you to join a team'.format(user['firstname'],
                                                                                                  user['lastname'])
        sender = CONFIG.MAIL_FROM_ID
        recipient = invitation.recipient_email
        confirmation_token = Invitation.generate_confirmation_token(invitation.id)
        token_confirm_url = '{}/validatetoken/{}'.format(app_url, confirmation_token)
        template = ENV.get_template('email_templates/business_invitation_email.html')

        sent_response = send_email(subject, sender, recipient,
                                   template.render(invitation=invitation,
                                                   url=token_confirm_url,
                                                   user=user,
                                                   org_name=org_name,
                                                   logo_url=f'{app_url}/{CONFIG.REGISTRIES_LOGO_IMAGE_NAME}'))
        if not sent_response:
            invitation.invitation_status_code = 'FAILED'
            invitation.save()
            current_app.logger.debug('>send_invitation failed')
            raise BusinessException(Error.FAILED_INVITATION, None)
        current_app.logger.debug('>send_invitation')

    @staticmethod
    def generate_confirmation_token(invitation_id):
        """Generate the token to be sent in the email."""
        serializer = URLSafeTimedSerializer(CONFIG.EMAIL_TOKEN_SECRET_KEY)
        return serializer.dumps(invitation_id, salt=CONFIG.EMAIL_SECURITY_PASSWORD_SALT)

    @staticmethod
    def validate_token(token):
        """Check whether the passed token is valid."""
        serializer = URLSafeTimedSerializer(CONFIG.EMAIL_TOKEN_SECRET_KEY)
        token_valid_for = int(CONFIG.TOKEN_EXPIRY_PERIOD) * 3600 * 24 if CONFIG.TOKEN_EXPIRY_PERIOD else 3600 * 24 * 7
        try:
            invitation_id = serializer.loads(token, salt=CONFIG.EMAIL_SECURITY_PASSWORD_SALT, max_age=token_valid_for)
        except:  # noqa: E722
            raise BusinessException(Error.EXPIRED_INVITATION, None)

        invitation: InvitationModel = InvitationModel.find_invitation_by_id(invitation_id)

        if invitation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if invitation.invitation_status_code == 'ACCEPTED':
            raise BusinessException(Error.ACTIONED_INVITATION, None)
        if invitation.invitation_status_code == 'EXPIRED':
            raise BusinessException(Error.EXPIRED_INVITATION, None)

        return invitation_id

    @staticmethod
    def notify_admin(user, invitation_id, membership_id, invitation_origin):
        """Admins should be notified if user has responded to invitation."""
        current_app.logger.debug('<notify_admin')
        admin_list = UserService.get_admins_for_membership(membership_id)
        invitation: InvitationModel = InvitationModel.find_invitation_by_id(invitation_id)
        context_path = CONFIG.AUTH_WEB_TOKEN_CONFIRM_PATH
        admin_emails = ''
        for contact in admin_list:
            if contact.contacts:
                admin_emails = contact.contacts[0].contact.email + ' ' + admin_emails

        Invitation.send_admin_notification(user.as_dict(),
                                           '{}/{}'.format(invitation_origin, context_path),
                                           admin_emails, invitation.membership[0].org.name)
        current_app.logger.debug('>notify_admin')
        return Invitation(invitation)

    @staticmethod
    def accept_invitation(invitation_id, user, origin):
        """Add user, role and org from the invitation to membership."""
        current_app.logger.debug('>accept_invitation')
        invitation: InvitationModel = InvitationModel.find_invitation_by_id(invitation_id)

        if invitation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if invitation.invitation_status_code == 'ACCEPTED':
            raise BusinessException(Error.ACTIONED_INVITATION, None)
        if invitation.invitation_status_code == 'EXPIRED':
            raise BusinessException(Error.EXPIRED_INVITATION, None)
        # TODO : isnt this only one?remove for loop
        for membership in invitation.membership:
            membership_model = MembershipModel()
            membership_model.org_id = membership.org_id
            membership_model.user_id = user.identifier
            membership_model.membership_type = membership.membership_type
            # user needs to get approval
            is_auto_approval = OrgSettingsModel.is_admin_auto_approved_invitees(membership.org_id)
            if is_auto_approval:
                membership_model.status = Status.ACTIVE.value
            else:
                membership_model.status = Status.PENDING_APPROVAL.value
            membership_model.save()
            if not is_auto_approval:
                try:
                    Invitation.notify_admin(user, invitation_id, membership_model.id, origin)
                except BusinessException as exception:
                    current_app.logger.error('<send_notification_to_admin failed', exception.message)
        invitation.accepted_date = datetime.now()
        invitation.invitation_status = InvitationStatusModel.get_status_by_code('ACCEPTED')
        invitation.save()
        current_app.logger.debug('<accept_invitation')
        return Invitation(invitation)

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


import urllib

from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from jinja2 import Environment, FileSystemLoader

from sbc_common_components.tracing.service_tracing import ServiceTracing
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Invitation as InvitationModel
from auth_api.schemas import InvitationSchema
from auth_api.models import Membership as MembershipModel
from config import get_named_config
from .notification import Notification


ENV = Environment(loader=FileSystemLoader('.'))
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
    def create_invitation(invitation_info: dict, user):
        """Create a new invitation."""
        invitation = InvitationModel.create_from_dict(invitation_info, user.identifier)
        invitation.save()
        Invitation.send_invitation(invitation, user.as_dict())
        return Invitation(invitation)

    def update_invitation(self, user):
        """Update the specified invitation with new data."""
        updated_invitation = self._model.update_invitation_as_retried()
        Invitation.send_invitation(updated_invitation, user.as_dict())
        return Invitation(updated_invitation)

    @staticmethod
    def delete_invitation(invitation_id):
        """Delete the specified invitation."""
        invitation = InvitationModel.find_invitation_by_id(invitation_id)
        if invitation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        invitation.delete()

    @staticmethod
    def get_invitations(user_id, status):
        """Get invitations sent by a user."""
        collection = []
        if status == 'ALL':
            invitations = InvitationModel.find_invitations_by_user(user_id)
        elif status == 'PENDING':
            invitations = InvitationModel.find_pending_invitations_by_user(user_id)
        else:
            invitations = InvitationModel.find_invitations_by_status(user_id, status)
        for invitation in invitations:
            collection.append(Invitation(invitation).as_dict())
        return collection

    @staticmethod
    def find_invitation_by_id(invitation_id):
        """Find an existing invitation with the provided id."""
        if invitation_id is None:
            return None

        invitation = InvitationModel.find_invitation_by_id(invitation_id)
        if not invitation:
            return None

        return Invitation(invitation)

    @staticmethod
    def send_invitation(invitation: InvitationModel, user):
        """Send the email notification."""
        subject = '[BC Registries & Online Services] {} {} has invited you to join a team'.format(user['firstname'],
                                                                                                  user['lastname'])
        sender = CONFIG.MAIL_FROM_ID
        recipient = invitation.recipient_email
        confirmation_token = Invitation.generate_confirmation_token(invitation.id)
        token_confirm_url = '{}/validatetoken/{}'.format(CONFIG.AUTH_WEB_TOKEN_CONFIRM_URL, confirmation_token)
        template = ENV.get_template('email_templates/business_invitation_email.html')
        try:
            Notification.send_email(subject, sender, recipient, template.render(invitation=invitation,
                                                                                url=token_confirm_url, user=user))
        except:
            invitation.invitation_status_code = 'FAILED'
            invitation.save()
            raise BusinessException(Error.FAILED_INVITATION, None)

    @staticmethod
    def generate_confirmation_token(invitation_id):
        """Generate the token to be sent in the email."""
        serializer = URLSafeTimedSerializer(CONFIG.EMAIL_TOKEN_SECRET_KEY)
        return serializer.dumps(invitation_id, salt=CONFIG.EMAIL_SECURITY_PASSWORD_SALT)

    @staticmethod
    def validate_token(token):
        """Check whether the passed token is valid."""
        serializer = URLSafeTimedSerializer(CONFIG.EMAIL_TOKEN_SECRET_KEY)
        token_valid_for = int(CONFIG.TOKEN_EXPIRY_PERIOD)*3600*24 if CONFIG.TOKEN_EXPIRY_PERIOD else 3600*24*7
        try:
            invitation_id = serializer.loads(token, salt=CONFIG.EMAIL_SECURITY_PASSWORD_SALT, max_age=token_valid_for)
        except:
            raise BusinessException(Error.EXPIRED_INVITATION, None)
        return invitation_id

    @staticmethod
    def accept_invitation(invitation_id, user_id):
        """Add user, role and org from the invitation to membership."""
        invitation: InvitationModel = InvitationModel.find_invitation_by_id(invitation_id)
        if invitation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if invitation.invitation_status_code == 'ACCEPTED':
            raise BusinessException(Error.ACTIONED_INVITATION, None)
        if invitation.invitation_status_code == 'EXPIRED':
            raise BusinessException(Error.EXPIRED_INVITATION, None)
        for membership in invitation.membership:
            membership_model = MembershipModel()
            membership_model.org_id = membership.org_id
            membership_model.user_id = user_id
            membership_model.membership_type_code = membership.membership_type_code
            membership_model.flush()
        invitation.accepted_date = datetime.now()
        invitation.invitation_status_code = 'ACCEPTED'
        invitation.flush()
        MembershipModel.commit()
        return Invitation(invitation)

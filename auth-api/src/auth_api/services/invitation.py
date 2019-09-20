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

from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Invitation as InvitationModel
from auth_api.schemas import InvitationSchema
from config import get_named_config

from .notification import Notification


ENV = Environment(loader=FileSystemLoader('.'))


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
    def create_invitation(invitation_info: dict, user_id):
        """Create a new invitation."""
        invitation = InvitationModel.create_from_dict(invitation_info, user_id)
        invitation.save()
        Invitation.send_invitation(invitation)
        return Invitation(invitation)

    @staticmethod
    def get_invitations(user_id):
        """Get invitations sent by a user."""
        collection = []
        invitations = InvitationModel.find_invitations_by_user(user_id)
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
    def delete_invitation(invitation_id):
        """Delete the specified invitation."""
        invitation = InvitationModel.find_invitation_by_id(invitation_id)
        if invitation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        invitation.delete()

    @staticmethod
    def send_invitation(invitation: InvitationModel):
        """Send the email notification."""
        config = get_named_config()
        subject = 'Business Invitation'
        sender = config.MAIL_FROM_ID
        recipient = invitation.recipient_email
        template = ENV.get_template('email_templates/business_invitation_email.html')
        Notification.send_email(subject, sender, recipient,
                                template.render(invitation=invitation))

    def update_invitation(self, invitation):
        """Update the specified invitation with new data."""
        self._model.update_invitation(invitation)
        return self

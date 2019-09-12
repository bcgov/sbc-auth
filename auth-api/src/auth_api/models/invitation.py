# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This model manages a Invitation item in the Auth Service."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_model import BaseModel
from .invitation_membership import InvitationMembership
from .invite_status import InvitationStatus


class Invitation(BaseModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """Model for a Invitation record."""

    __tablename__ = 'invitation'

    id = Column(Integer, primary_key=True)
    sender_id = Column(ForeignKey('user.id'), nullable=False)
    recipient_email = Column(String(100), nullable=False)
    sent_date = Column(DateTime, nullable=False)
    accepted_date = Column(DateTime, nullable=True)
    invitation_status_code = Column(ForeignKey('invitation_status.code'), nullable=False, default='PENDING')

    status = relationship('InvitationStatus', foreign_keys=[invitation_status_code])
    sender = relationship('User', foreign_keys=[sender_id])
    membership = relationship('InvitationMembership', cascade='all,delete')

    @classmethod
    def create_from_dict(cls, invitation_info: dict, user_id):
        """Create a new Invitation from the provided dictionary."""
        if invitation_info:
            invitation = Invitation()
            invitation.sender_id = user_id
            invitation.recipient_email = invitation_info['recipientEmail']
            invitation.sent_date = invitation_info['sentDate']
            invitation.status = InvitationStatus.get_default_status()

            for member in invitation_info['membership']:
                invitation_membership = InvitationMembership()
                invitation_membership.org_id = member['orgId']
                invitation_membership.membership_type_code = member['membershipType']
                invitation.membership.append(invitation_membership)

            invitation.save()
            return invitation
        return None

    @classmethod
    def find_invitations_by_user(cls, user_id):
        """Find all invitation sent by the given user."""
        return cls.query.filter_by(sender_id=user_id).all()

    @classmethod
    def find_invitation_by_id(cls, invitation_id):
        """Find an invitation record that matches the id."""
        return cls.query.filter_by(id=invitation_id).first()

    def update_invitation(self, invitation_info: dict):
        """Update this invitation with the new data."""
        if invitation_info:
            self.accepted_date = invitation_info['acceptedDate']
            self.invitation_status_code = invitation_info['status']
            self.save()

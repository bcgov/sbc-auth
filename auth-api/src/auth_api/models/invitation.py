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

from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from config import get_named_config

from .base_model import BaseModel
from .db import db
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
    token = Column(String(100), nullable=True)  # stores the one time invitation token
    invitation_status_code = Column(ForeignKey('invitation_status.code'), nullable=False, default='PENDING')
    type = Column(ForeignKey('invitation_type.code'), nullable=False, default='STANDARD')

    invitation_status = relationship('InvitationStatus', foreign_keys=[invitation_status_code])
    sender = relationship('User', foreign_keys=[sender_id])
    membership = relationship('InvitationMembership', cascade='all,delete')
    login_source = Column(String(20), nullable=True)

    @hybrid_property
    def expires_on(self):
        """Calculate the expiry date based on the config value."""
        if self.invitation_status_code == 'PENDING':
            return self.sent_date + timedelta(days=int(get_named_config().TOKEN_EXPIRY_PERIOD))
        return None

    @hybrid_property
    def status(self):
        """Calculate the status based on the config value."""
        current_time = datetime.now()
        if self.invitation_status_code == 'PENDING':
            expiry_time = self.sent_date + timedelta(days=int(get_named_config().TOKEN_EXPIRY_PERIOD))
            if current_time >= expiry_time:
                return 'EXPIRED'
        return self.invitation_status_code

    @classmethod
    def create_from_dict(cls, invitation_info: dict, user_id, invitation_type):
        """Create a new Invitation from the provided dictionary."""
        if invitation_info:
            invitation = Invitation()
            invitation.sender_id = user_id
            invitation.type = invitation_type
            invitation.recipient_email = invitation_info['recipientEmail']
            invitation.sent_date = datetime.now()
            invitation.invitation_status = InvitationStatus.get_default_status()

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

    @classmethod
    def find_invitations_by_org(cls, org_id, status=None):
        """Find all invitations sent for specific org filtered by status."""
        results = cls.query.filter(Invitation.membership.any(InvitationMembership.org_id == org_id))
        return results.filter(Invitation.status == status.value).all() if status else results.all()

    @staticmethod
    def find_pending_invitations_by_user(user_id):
        """Find all invitations that are not in accepted state."""
        return db.session.query(Invitation). \
            filter(Invitation.sender_id == user_id). \
            filter(Invitation.invitation_status_code != 'ACCEPTED').all()

    @staticmethod
    def find_pending_invitations_by_org(org_id):
        """Find all invitations that are not in accepted state."""
        return db.session.query(Invitation) \
            .filter(Invitation.membership.any(InvitationMembership.org_id == org_id)) \
            .filter(Invitation.invitation_status_code != 'ACCEPTED').all()

    @staticmethod
    def find_invitations_by_status(user_id, status):
        """Find all invitations that are not in accepted state."""
        return db.session.query(Invitation). \
            filter(Invitation.sender_id == user_id). \
            filter(Invitation.invitation_status_code == status).all()

    def update_invitation_as_retried(self):
        """Update this invitation with the new data."""
        self.sent_date = datetime.now()
        self.invitation_status = InvitationStatus.get_default_status()
        self.save()
        return self

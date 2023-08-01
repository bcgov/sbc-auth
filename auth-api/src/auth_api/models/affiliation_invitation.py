# Copyright © 2023 Province of British Columbia
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
"""This model manages an Affiliation Invitation item in the Auth Service."""

from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, or_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from auth_api.config import get_named_config
from auth_api.utils.enums import InvitationStatus as InvitationStatuses
from auth_api.utils.enums import AffiliationInvitationType as AffiliationInvitationTypeEnum
from .affiliation_invitation_type import AffiliationInvitationType

from .base_model import BaseModel
from .db import db
from .invite_status import InvitationStatus


class AffiliationInvitation(BaseModel):  # pylint: disable=too-many-instance-attributes
    """Model for an Affiliation Invitation record."""

    __tablename__ = 'affiliation_invitations'

    id = Column(Integer, primary_key=True)
    from_org_id = Column(ForeignKey('orgs.id'), nullable=False, index=True)
    to_org_id = Column(ForeignKey('orgs.id'), nullable=False, index=True)
    entity_id = Column(ForeignKey('entities.id'), nullable=False, index=True)
    affiliation_id = Column(ForeignKey('affiliations.id'), nullable=True, index=True)
    sender_id = Column(ForeignKey('users.id'), nullable=False)
    approver_id = Column(ForeignKey('users.id'), nullable=True)
    recipient_email = Column(String(100), nullable=False)
    sent_date = Column(DateTime, nullable=False)
    accepted_date = Column(DateTime, nullable=True)
    token = Column(String(100), nullable=True)  # stores the one time affiliation invitation token
    login_source = Column(String(20), nullable=True)
    invitation_status_code = Column(ForeignKey('invitation_statuses.code'), nullable=False, default='PENDING')
    type = Column(ForeignKey('affiliation_invitation_types.code'), nullable=False, default='EMAIL')
    additional_message = Column(String(4000), nullable=True)

    invitation_status = relationship('InvitationStatus', foreign_keys=[invitation_status_code])
    sender = relationship('User', foreign_keys=[sender_id])
    entity = relationship('Entity', foreign_keys=[entity_id], lazy='select')
    from_org = relationship('Org', foreign_keys=[from_org_id], lazy='select')
    to_org = relationship('Org', foreign_keys=[to_org_id], lazy='select')
    affiliation = relationship('Affiliation', foreign_keys=[affiliation_id], lazy='select')

    @hybrid_property
    def expires_on(self):
        """Calculate the expiry date based on the config value."""
        if self.invitation_status_code == InvitationStatuses.PENDING.value:
            return self.sent_date + timedelta(minutes=int(get_named_config().AFFILIATION_TOKEN_EXPIRY_PERIOD_MINS))
        return None

    @hybrid_property
    def status(self):
        """Calculate the status based on the config value."""
        current_time = datetime.now()
        # if type is REQUEST do not expire (only cancel through todo)
        if self.type == AffiliationInvitationTypeEnum.REQUEST.value:
            return self.invitation_status_code

        if self.invitation_status_code == InvitationStatuses.PENDING.value:
            expiry_time = self.sent_date + timedelta(
                minutes=int(get_named_config().AFFILIATION_TOKEN_EXPIRY_PERIOD_MINS))
            if current_time >= expiry_time:
                return InvitationStatuses.EXPIRED.value
        return self.invitation_status_code

    @classmethod
    def create_from_dict(cls, invitation_info: dict, user_id, affiliation_id=None):
        """Create a new Invitation from the provided dictionary."""
        if not invitation_info:
            return None

        affiliation_invitation = AffiliationInvitation()
        affiliation_invitation.sender_id = user_id
        affiliation_invitation.affiliation_id = affiliation_id
        affiliation_invitation.from_org_id = invitation_info['fromOrgId']
        affiliation_invitation.to_org_id = invitation_info['toOrgId']
        affiliation_invitation.entity_id = invitation_info['entityId']
        affiliation_invitation.recipient_email = invitation_info['recipientEmail']
        affiliation_invitation.sent_date = datetime.now()
        affiliation_invitation.type = invitation_info.get('type')
        affiliation_invitation.invitation_status = InvitationStatus.get_default_status()
        affiliation_invitation.additional_message = invitation_info.get('additional_message', None)

        if affiliation_invitation.type is None:
            affiliation_invitation.type = AffiliationInvitationType.get_default_type().code

        affiliation_invitation.save()
        return affiliation_invitation

    # pylint: disable=too-many-arguments
    @classmethod
    def filter_by(cls,
                  from_org_id=None,
                  to_org_id=None,
                  sender_id=None,
                  approver_id=None,
                  entity_id=None,
                  affiliation_id=None,
                  status_codes=None,
                  invitation_types=None
                  ) -> list:
        """Filter list of Affiliation Invitations by provided filters. At least one filter needs to be provided."""
        results = db.session.query(AffiliationInvitation)
        filter_set = False

        if from_org_id is not None:
            results = results.filter(AffiliationInvitation.from_org_id == from_org_id)
            filter_set = True

        if to_org_id is not None:
            results = results.filter(AffiliationInvitation.to_org_id == to_org_id)
            filter_set = True

        if sender_id is not None:
            results = results.filter(AffiliationInvitation.sender_id == sender_id)
            filter_set = True

        if approver_id is not None:
            results = results.filter(AffiliationInvitation.approver_id == approver_id)
            filter_set = True

        if entity_id is not None:
            results = results.filter(AffiliationInvitation.entity_id == entity_id)
            filter_set = True

        if affiliation_id is not None:
            results = results.filter(AffiliationInvitation.affiliation_id == affiliation_id)
            filter_set = True

        if status_codes is not None and status_codes:
            results = results.filter(AffiliationInvitation.status.in_(status_codes))  # pylint: disable=no-member
            filter_set = True

        if invitation_types is not None and status_codes:
            results = results.filter(AffiliationInvitation.type.in_(invitation_types))
            filter_set = True

        if not filter_set:
            raise ValueError('At least one filter has to be set!')

        return results.all()

    @classmethod
    def find_invitation_by_id(cls, invitation_id):
        """Find an affiliation invitation record that matches the id."""
        return cls.query.filter_by(id=invitation_id).first()

    @classmethod
    def find_invitations_from_org(cls, org_id, status=None):
        """Find all affiliation invitations sent from a specific org filtered by status."""
        results = db.session.query(AffiliationInvitation) \
            .filter(AffiliationInvitation.from_org_id == org_id)
        return results.filter(AffiliationInvitation.status == status.value).all() if status else results.all()

    @classmethod
    def find_invitations_to_org(cls, org_id, status=None):
        """Find all affiliation invitations sent to a specific org filtered by status."""
        results = db.session.query(AffiliationInvitation) \
            .filter(AffiliationInvitation.to_org_id == org_id)
        return results.filter(AffiliationInvitation.status == status.value).all() if status else results.all()

    @classmethod
    def find_invitations_by_entity(cls, entity_id, status=None):
        """Find all affiliation invitations sent for specific entity filtered by status."""
        results = db.session.query(AffiliationInvitation) \
            .filter(AffiliationInvitation.entity_id == entity_id)
        return results.filter(AffiliationInvitation.status == status.value).all() if status else results.all()

    @classmethod
    def find_invitations_by_affiliation(cls, affiliation_id):
        """Find all affiliation invitations associated to an affiliation."""
        return cls.query.filter_by(affiliation_id=affiliation_id).all()

    @staticmethod
    def find_invitations_by_org_entity_ids(from_org_id, to_org_id, entity_id):
        """Find all affiliation invitation for org and entity ids."""
        return db.session.query(AffiliationInvitation) \
            .filter(AffiliationInvitation.from_org_id == from_org_id) \
            .filter(AffiliationInvitation.to_org_id == to_org_id) \
            .filter(AffiliationInvitation.entity_id == entity_id) \
            .filter(or_(AffiliationInvitation.invitation_status_code == InvitationStatuses.PENDING.value,
                        AffiliationInvitation.invitation_status_code == InvitationStatuses.ACCEPTED.value)).all()

    def update_invitation_as_retried(self, sender_id):
        """Update this affiliation invitation with the new data."""
        self.sender_id = sender_id
        self.sent_date = datetime.now()
        self.invitation_status = InvitationStatus.get_default_status()
        self.save()
        return self

    def set_status(self, new_status_code):
        """Set status of the Affiliation Invitation to provided status code."""
        self.invitation_status = InvitationStatus.get_status_by_code(new_status_code)
        self.save()
        return self

    @classmethod
    def find_all_related_to_org(cls, org_id, status_filters=None, types_filter=None):
        """Return all affiliation invitations that are related to the org (from org or to org) filtered by statuses."""
        results = db.session.query(AffiliationInvitation) \
            .filter(
            or_(AffiliationInvitation.to_org_id == org_id, AffiliationInvitation.from_org_id == org_id)
        )

        if status_filters is not None:
            results = results.filter(AffiliationInvitation.status.in_(status_filters))  # pylint: disable=no-member

        if types_filter is not None:
            results = results.filter(AffiliationInvitation.type.in_(types_filter))

        return results.all()

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
from sqlalchemy.orm import relationship, aliased

from auth_api.config import get_named_config
from auth_api.utils.enums import InvitationStatus as InvitationStatuses
from auth_api.models.org import Org as OrgModel
from auth_api.models.entity import Entity as EntityModel
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

    @classmethod
    def find_invitations_by_sender(cls, user_id):
        """Find all affiliation invitations sent by the given user."""
        return cls.query.filter_by(sender_id=user_id).all()

    @classmethod
    def find_invitations_by_approver(cls, user_id):
        """Find all affiliation invitations approved by the given user."""
        return cls.query.filter_by(approver_id=user_id).all()

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

    @staticmethod
    def find_pending_invitations_by_sender(user_id):
        """Find all affiliation invitations that are in pending state."""
        return db.session.query(AffiliationInvitation). \
            filter(AffiliationInvitation.sender_id == user_id). \
            filter(AffiliationInvitation.invitation_status_code == InvitationStatuses.PENDING.value).all()

    @staticmethod
    def find_pending_invitations_by_from_org(org_id):
        """Find all affiliation invitations that are in pending state from an org."""
        return db.session.query(AffiliationInvitation) \
            .filter(AffiliationInvitation.from_org_id == org_id) \
            .filter(AffiliationInvitation.invitation_status_code == InvitationStatuses.PENDING.value).all()

    @staticmethod
    def find_pending_invitations_by_to_org(org_id):
        """Find all affiliation invitations that are in pending state to an org."""
        return db.session.query(AffiliationInvitation) \
            .filter(AffiliationInvitation.to_org_id == org_id) \
            .filter(AffiliationInvitation.invitation_status_code == InvitationStatuses.PENDING.value).all()

    @staticmethod
    def find_pending_invitations_by_entity(entity_id):
        """Find all affiliation invitations that are in pending state."""
        return db.session.query(AffiliationInvitation) \
            .filter(AffiliationInvitation.entity_id == entity_id) \
            .filter(AffiliationInvitation.invitation_status_code == InvitationStatuses.PENDING.value).all()

    @staticmethod
    def find_invitations_by_status(user_id, status):
        """Find all affiliation invitations for a sender filtered by status."""
        return db.session.query(AffiliationInvitation). \
            filter(AffiliationInvitation.sender_id == user_id). \
            filter(AffiliationInvitation.invitation_status_code == status).all()

    def update_invitation_as_retried(self, sender_id):
        """Update this affiliation invitation with the new data."""
        self.sender_id = sender_id
        self.sent_date = datetime.now()
        self.invitation_status = InvitationStatus.get_default_status()
        self.save()
        return self

    def expire_invitation(self):
        """Update this affiliation invitation with the new data."""
        self.invitation_status = InvitationStatus.get_status_by_code(InvitationStatuses.EXPIRED.value)
        self.save()
        return self

    def fail_invitation(self):
        self.invitation_status = InvitationStatus.get_status_by_code(InvitationStatuses.FAILED.value)
        self.save()
        return self

    @classmethod
    def find_all_related_to_org(cls, org_id, status_filters=None, types_filter=None):
        """Gets all affiliation invitations that are related to the org (either from or to org) filtered by statuses"""
        from_org = aliased(OrgModel)
        to_org = aliased(OrgModel)
        entity = aliased(EntityModel)
        results = db.session.query(AffiliationInvitation, from_org, to_org, entity) \
            .join(from_org, AffiliationInvitation.from_org_id == from_org.id) \
            .join(to_org, AffiliationInvitation.to_org_id == to_org.id) \
            .join(entity, AffiliationInvitation.entity_id == entity.id) \
            .filter(
            or_(AffiliationInvitation.to_org_id == org_id, AffiliationInvitation.from_org_id == org_id)
        )

        if status_filters is not None:
            results = results.filter(AffiliationInvitation.status.in_(status_filters))

        if types_filter is not None:
            results = results.filter(AffiliationInvitation.type.in_(types_filter))

        return results.all()

    @classmethod
    def find_all_sent_to_org_for_entity(cls, to_org_id, entity_id, status_filters=None, types_filter=None):
        from_org = aliased(OrgModel)
        to_org = aliased(OrgModel)
        entity = aliased(EntityModel)
        results = db.session.query(AffiliationInvitation, from_org, to_org, entity) \
            .join(from_org, AffiliationInvitation.from_org_id == from_org.id) \
            .join(to_org, AffiliationInvitation.to_org_id == to_org.id) \
            .join(entity, AffiliationInvitation.entity_id == entity.id) \
            .filter(AffiliationInvitation.entity_id == entity_id) \
            .filter(AffiliationInvitation.to_org_id == to_org_id)

        if status_filters is not None:
            results = results.filter(AffiliationInvitation.status.in_(status_filters))

        if types_filter is not None:
            results = results.filter(AffiliationInvitation.type.in_(types_filter))

        return results.all()

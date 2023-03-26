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
"""This model manages a Membership item in the Auth Service.

The Membership object connects User models to one or more Org models.
"""

from __future__ import annotations

from typing import List

from sqlalchemy import Column, ForeignKey, Integer, and_, desc, func
from sqlalchemy.orm import relationship

from auth_api.utils.enums import OrgType, Status
from auth_api.utils.roles import ADMIN, COORDINATOR, USER, VALID_ORG_STATUSES, VALID_STATUSES
from .base_model import VersionedModel
from .db import db
from .membership_status_code import MembershipStatusCode
from .membership_type import MembershipType
from .org import Org as OrgModel


class Membership(VersionedModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """Model for a Membership model.  Associates Users and Orgs."""

    __tablename__ = 'memberships'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    org_id = Column(ForeignKey('orgs.id'), nullable=False, index=True)
    membership_type_code = Column(
        ForeignKey('membership_types.code'), nullable=False
    )
    status = Column(
        ForeignKey('membership_status_codes.id'), index=True
    )
    membership_type = relationship('MembershipType', foreign_keys=[membership_type_code], lazy='select')
    membership_status = relationship('MembershipStatusCode', foreign_keys=[status], lazy='select')
    user = relationship('User', foreign_keys=[user_id], lazy='select')
    org = relationship('Org', foreign_keys=[org_id], lazy='select')

    def __init__(self, **kwargs):
        """Initialize a new membership."""
        self.org_id = kwargs.get('org_id')
        self.user_id = kwargs.get('user_id')

        self.membership_type_code = kwargs.get('membership_type_code')
        if self.membership_type_code is None:
            self.membership_type = MembershipType.get_default_type()

        self.status = kwargs.get('membership_type_status')

        if self.status is None:
            self.status = MembershipStatusCode.get_default_type()
        else:
            self.status = kwargs.get('membership_type_status')

    @classmethod
    def find_membership_by_id(cls, membership_id) -> Membership:
        """Find the first membership with the given id and return it."""
        return cls.query.filter_by(id=membership_id).first()

    @classmethod
    def find_members_by_org_id(cls, org_id) -> List[Membership]:
        """Return all members of the org with a status."""
        return cls.query.filter_by(org_id=org_id).all()

    @classmethod
    def get_pending_members_count_by_org_id(cls, org_id) -> int:
        """Return the count of pending members."""
        query = db.session.query(Membership).filter(
            and_(Membership.status == Status.PENDING_APPROVAL.value)). \
            join(OrgModel).filter(OrgModel.id == org_id)
        count_q = query.statement.with_only_columns([func.count()]).order_by(None)
        count = query.session.execute(count_q).scalar()
        return count

    @classmethod
    def find_members_by_org_id_by_status_by_roles(cls, org_id, roles, status=Status.ACTIVE.value) -> List[Membership]:
        """Return all members of the org with a status."""
        return db.session.query(Membership).filter(
            and_(Membership.status == status, Membership.membership_type_code.in_(roles))). \
            join(OrgModel).filter(OrgModel.id == org_id).all()

    @classmethod
    def find_orgs_for_user(cls, user_id, valid_statuses=VALID_STATUSES) -> List[OrgModel]:
        """Find the orgs for a user."""
        records = cls.query \
            .join(OrgModel) \
            .filter(cls.user_id == user_id) \
            .filter(cls.status.in_(valid_statuses)) \
            .filter(OrgModel.status_code.in_(VALID_ORG_STATUSES)) \
            .all()

        return list(map(lambda x: x.org, records))

    @classmethod
    def find_active_staff_org_memberships_for_user(cls, user_id) -> List[Membership]:
        """Find staff orgs memberships for a user."""
        return cls.query \
            .join(OrgModel) \
            .filter(cls.user_id == user_id) \
            .filter(cls.status == Status.ACTIVE.value) \
            .filter(OrgModel.status_code.in_(VALID_ORG_STATUSES)) \
            .filter(OrgModel.type_code == OrgType.STAFF.value) \
            .all()

    @classmethod
    def add_membership_for_staff(cls, user_id):
        """Add staff membership."""
        if (staff_orgs := OrgModel.find_by_org_type(OrgType.STAFF.value)):
            membership = cls.find_membership_by_user_and_org(user_id, staff_orgs[0].id)
            if not membership:
                membership = Membership(org_id=staff_orgs[0].id, user_id=user_id, membership_type_code=USER)
            membership.status = Status.ACTIVE.value
            membership.save()

    @classmethod
    def remove_membership_for_staff(cls, user_id):
        """Remove staff membership."""
        staff_memberships = cls.find_active_staff_org_memberships_for_user(user_id)
        for staff_membership in staff_memberships:
            staff_membership.status = Status.INACTIVE.value
            staff_membership.save()

    @classmethod
    def find_membership_by_user_and_org(cls, user_id, org_id) -> Membership:
        """Get the membership for the specified user and org."""
        records = cls.query \
            .filter(cls.user_id == user_id) \
            .filter(cls.org_id == org_id) \
            .filter(cls.status.in_(VALID_STATUSES)) \
            .order_by(desc(Membership.created)) \
            .first()

        return records

    @classmethod
    def find_membership_by_userid(cls, user_id) -> Membership:
        """Get the membership for the specified user."""
        records = cls.query \
            .filter(cls.user_id == user_id) \
            .order_by(desc(Membership.created)) \
            .first()

        return records

    @classmethod
    def find_memberships_by_user_ids(cls, user_id) -> List[Membership]:
        """Get the memberships for the specified user ids."""
        records = cls.query \
            .filter(cls.user_id == user_id) \
            .order_by(desc(Membership.created)) \
            .all()

        return records

    @classmethod
    def find_membership_by_user_and_org_all_status(cls, user_id, org_id) -> Membership:
        """Get the membership for the specified user and org with all membership statuses."""
        records = cls.query \
            .filter(cls.user_id == user_id) \
            .filter(cls.org_id == org_id) \
            .order_by(desc(Membership.created)) \
            .first()

        return records

    @classmethod
    def get_count_active_owner_org_id(cls, org_id) -> int:
        """Return the count of pending members."""
        query = db.session.query(Membership).filter(
            and_(Membership.org_id == org_id, Membership.status == Status.ACTIVE.value,
                 Membership.membership_type_code == ADMIN)). \
            join(OrgModel).filter(OrgModel.id == org_id)
        count_q = query.statement.with_only_columns([func.count()]).order_by(None)
        count = query.session.execute(count_q).scalar()
        return count

    @classmethod
    def check_if_active_admin_or_owner_org_id(cls, org_id, user_id) -> int:
        """Return the count of pending members."""
        query = db.session.query(Membership).filter(
            and_(Membership.user_id == user_id, Membership.org_id == org_id, Membership.status == Status.ACTIVE.value,
                 Membership.membership_type_code.in_((ADMIN, COORDINATOR)))). \
            join(OrgModel).filter(OrgModel.id == org_id)
        count_q = query.statement.with_only_columns([func.count()]).order_by(None)
        count = query.session.execute(count_q).scalar()
        return count

    def reset(self):
        """Reset member."""
        if self.membership_type_code == 'ADMIN':
            # if an org only have one admin, we need to prompt a coordiantor or user to admin to avoid failure.
            members = self.find_members_by_org_id_by_status_by_roles(self.org_id, (ADMIN, ADMIN))
            count_members = len(members)
            if count_members == 1:
                members = self.find_members_by_org_id_by_status_by_roles(self.org_id, (COORDINATOR, USER))
                for member in members:
                    member.membership_type_code = 'ADMIN'
                    db.session.add(member)
                    db.session.commit()
                    member.modified_by = None
                    member.modified_by_id = None
                    db.session.add(member)
                    db.session.commit()
                    break

        super().reset()

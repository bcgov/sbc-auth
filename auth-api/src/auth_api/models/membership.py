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

from sqlalchemy import Column, ForeignKey, Integer, and_, desc
from sqlalchemy.orm import relationship

from auth_api.utils.roles import VALID_STATUSES, Status

from .base_model import BaseModel
from .db import db
from .membership_status_code import MembershipStatusCode
from .membership_type import MembershipType
from .org import Org as OrgModel


class Membership(BaseModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """Model for a Membership model.  Associates Users and Orgs."""

    __tablename__ = 'membership'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    org_id = Column(ForeignKey('org.id'), nullable=False)
    membership_type_code = Column(
        ForeignKey('membership_type.code'), nullable=False
    )
    status = Column(
        ForeignKey('membership_status_code.id')
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
    def find_membership_by_id(cls, membership_id):
        """Find the first membership with the given id and return it."""
        return cls.query.filter_by(id=membership_id).first()

    @classmethod
    def find_members_by_org_id(cls, org_id):
        """Return all members of the org with a status."""
        return cls.query.filter_by(org_id=org_id).all()

    @classmethod
    def find_members_by_org_id_by_status_by_roles(cls, org_id, roles, status=Status.ACTIVE.value):
        """Return all members of the org with a status."""
        return db.session.query(Membership).filter(
            and_(Membership.status == status, Membership.membership_type_code.in_(roles))). \
            join(OrgModel).filter(OrgModel.id == org_id).all()

    @classmethod
    def find_orgs_for_user(cls, user_id):
        """Find the orgs for a user."""
        records = cls.query \
            .filter(cls.user_id == user_id) \
            .filter(cls.status.in_(VALID_STATUSES)) \
            .filter(OrgModel.status_code == 'ACTIVE') \
            .all()

        return list(map(lambda x: x.org, records))

    @classmethod
    def find_membership_by_user_and_org(cls, user_id, org_id):
        """Get the membership for the specified user and org."""
        return cls.query.filter_by(user_id=user_id, org_id=org_id).order_by(desc(Membership.created)).first()

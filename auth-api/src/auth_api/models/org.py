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
"""This manages an Org record, where an Org associates a User (via a Role) with one or more Entities.

Basic users will have an internal Org that is not created explicitly, but implicitly upon User account creation.
"""

from flask import current_app
from sqlalchemy import Column, ForeignKey, Integer, String, and_, func, Boolean
from sqlalchemy.orm import relationship

from auth_api.utils.roles import OrgStatus as OrgStatusEnum

from .base_model import BaseModel
from .org_status import OrgStatus
from .org_type import OrgType


class Org(BaseModel):  # pylint: disable=too-few-public-methods
    """Model for an Org record."""

    __tablename__ = 'org'

    id = Column(Integer, primary_key=True)
    type_code = Column(ForeignKey('org_type.code'), nullable=False)
    status_code = Column(ForeignKey('org_status.code'), nullable=False)
    name = Column(String(250), index=True)
    access_type = Column(String(250), index=True, nullable=True)  # for ANONYMOUS ACCESS
    billable = Column('billable', Boolean(), default=True, nullable=False)

    contacts = relationship('ContactLink', lazy='select')
    org_type = relationship('OrgType')
    org_status = relationship('OrgStatus')
    members = relationship('Membership', cascade='all,delete,delete-orphan', lazy='select')
    affiliated_entities = relationship('Affiliation', lazy='select')
    invitations = relationship('InvitationMembership', cascade='all,delete,delete-orphan', lazy='select')
    products = relationship('ProductSubscription', cascade='all,delete,delete-orphan', lazy='select')
    payment_settings = relationship('AccountPaymentSettings', cascade='all,delete,delete-orphan', lazy='select')

    @classmethod
    def create_from_dict(cls, org_info: dict):
        """Create a new Org from the provided dictionary."""
        if org_info:
            org = Org(**org_info)
            current_app.logger.debug(
                'Creating org from dictionary {}'.format(org_info)
            )
            if org.type_code:
                org.org_type = OrgType.get_type_for_code(org.type_code)
            else:
                org.org_type = OrgType.get_default_type()
            org.org_status = OrgStatus.get_default_status()
            org.save()
            return org
        return None

    @classmethod
    def find_by_org_id(cls, org_id):
        """Find an Org instance that matches the provided id."""
        return cls.query.filter_by(id=org_id).first()

    @classmethod
    def find_by_org_access_type(cls, org_type):
        """Find all orgs with the given type."""
        return cls.query.filter_by(access_type=org_type).all()

    @classmethod
    def find_similar_org_by_name(cls, name, org_id=None):
        """Find an Org instance that matches the provided name."""
        # TODO: add more fancy comparison
        query = cls.query.filter(Org.name.ilike(f'%{name}%'))
        if org_id:
            query = query.filter(Org.id != org_id)
        return query.first()

    @classmethod
    def get_count_of_org_created_by_user_id(cls, user_id):
        """Find the count of the organisations created by the user."""
        return cls.query.filter(and_(Org.created_by_id == user_id, Org.status_code == 'ACTIVE')).with_entities(
            func.count()).scalar()

    def update_org_from_dict(self, org_info: dict, exclude=('status_code', 'type_code')):
        """Update this org with the provided dictionary."""
        # Update from provided dictionary, but specify additional fields not to update.
        self.update_from_dict(**org_info, _exclude=exclude)
        self.save()

    def delete(self):
        """Deletes/Inactivates an org."""
        self.status_code = OrgStatusEnum.INACTIVE.value
        self.save()

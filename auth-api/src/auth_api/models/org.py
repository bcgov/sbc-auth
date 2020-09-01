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
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, and_, func
from sqlalchemy.orm import contains_eager, relationship

from auth_api.utils.enums import AccessType, InvitationStatus, InvitationType, OrgStatus as OrgStatusEnum
from auth_api.utils.roles import VALID_STATUSES

from .account_payment_settings import AccountPaymentSettings as AccountPaymentSettingsModel
from .base_model import VersionedModel
from .contact import Contact
from .contact_link import ContactLink
from .db import db
from .invitation import InvitationMembership
from .invitation import Invitation
from .org_status import OrgStatus
from .org_type import OrgType


class Org(VersionedModel):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Model for an Org record."""

    __tablename__ = 'org'

    id = Column(Integer, primary_key=True)
    type_code = Column(ForeignKey('org_type.code'), nullable=False)
    status_code = Column(ForeignKey('org_status.code'), nullable=False)
    name = Column(String(250), index=True)
    access_type = Column(String(250), index=True, nullable=True)  # for ANONYMOUS ACCESS
    billable = Column('billable', Boolean(), default=True, nullable=False)
    decision_made_by = Column(String(250))
    decision_made_on = Column(DateTime, nullable=True)

    contacts = relationship('ContactLink', lazy='select')
    org_type = relationship('OrgType')
    org_status = relationship('OrgStatus')
    members = relationship('Membership', cascade='all,delete,delete-orphan', lazy='select')
    affiliated_entities = relationship('Affiliation', lazy='select')
    invitations = relationship('InvitationMembership', cascade='all,delete,delete-orphan', lazy='select')
    products = relationship('ProductSubscription', cascade='all,delete,delete-orphan', lazy='select')
    payment_settings = relationship('AccountPaymentSettings', cascade='all,delete,delete-orphan',
                                    primaryjoin='and_(Org.id == AccountPaymentSettings.org_id, '
                                                'AccountPaymentSettings.is_active == True)', lazy='select')
    login_options = relationship('AccountLoginOptions', cascade='all,delete,delete-orphan',
                                 primaryjoin='and_(Org.id == AccountLoginOptions.org_id, '
                                             'AccountLoginOptions.is_active == True)', lazy='select')

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
            org.flush()

            return org
        return None

    @classmethod
    def find_by_org_id(cls, org_id):
        """Find an Org instance that matches the provided id."""
        return cls.query.filter_by(id=org_id).first()

    @classmethod
    def search_org(cls, access_type, name, status, bcol_account_id,  # pylint: disable=too-many-arguments
                   page: int, limit: int):
        """Find all orgs with the given type."""
        query = db.session.query(Org) \
            .outerjoin(ContactLink) \
            .outerjoin(Contact) \
            .options(contains_eager('contacts').contains_eager('contact'))

        if access_type:
            query = query.filter(Org.access_type.in_(access_type.split(',')))
        if name:
            query = query.filter(Org.name.ilike(f'%{name}%'))
        if status:
            query = query.filter(Org.status_code == status.upper())
            # If status is active, need to exclude the dir search orgs who haven't accepted the invitation yet
            if status == OrgStatusEnum.ACTIVE.value:
                pending_inv_subquery = db.session.query(Org.id) \
                    .outerjoin(InvitationMembership, InvitationMembership.org_id == Org.id) \
                    .outerjoin(Invitation, Invitation.id == InvitationMembership.invitation_id) \
                    .filter(Invitation.invitation_status_code == InvitationStatus.PENDING.value,
                            Invitation.type == InvitationType.DIRECTOR_SEARCH.value) \
                    .filter(Org.access_type == AccessType.ANONYMOUS.value)

                query = query.filter(Org.id.notin_(pending_inv_subquery))

        if bcol_account_id:
            query = query.join(AccountPaymentSettingsModel).filter(and_(
                AccountPaymentSettingsModel.bcol_account_id == bcol_account_id,
                AccountPaymentSettingsModel.is_active.is_(True)))

        query = query.order_by(Org.created.desc())

        # Add pagination
        pagination = query.paginate(per_page=limit, page=page)
        return pagination.items, pagination.total

    @classmethod
    def search_pending_activation_orgs(cls, name):
        """Find all orgs with the given type."""
        query = db.session.query(Org) \
            .outerjoin(InvitationMembership, InvitationMembership.org_id == Org.id) \
            .outerjoin(Invitation, Invitation.id == InvitationMembership.invitation_id) \
            .options(contains_eager('invitations').contains_eager('invitation')) \
            .filter(Invitation.invitation_status_code == InvitationStatus.PENDING.value,
                    Invitation.type == InvitationType.DIRECTOR_SEARCH.value,
                    Org.status_code == OrgStatusEnum.ACTIVE.value) \
            .filter(Org.access_type == AccessType.ANONYMOUS.value)

        if name:
            query = query.filter(Org.name.ilike(f'%{name}%'))

        query = query.order_by(Org.created.desc())

        orgs = query.all()
        return orgs, len(orgs)

    @classmethod
    def find_by_org_access_type(cls, org_type):
        """Find all orgs with the given type."""
        return cls.query.filter_by(access_type=org_type).all()

    @classmethod
    def find_similar_org_by_name(cls, name, org_id=None):
        """Find an Org instance that matches the provided name."""
        # TODO: add more fancy comparison
        query = cls.query.filter(Org.name.ilike(f'%{name}%')).filter(Org.status_code != OrgStatusEnum.INACTIVE.value)
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

    def reset(self):
        """Reset an org."""
        # Delete the record if no other member in this account, otherwise need to update the user.
        count_members = len([member for member in self.members if member.status in VALID_STATUSES])
        if count_members > 1 or len(self.affiliated_entities) >= 1:
            # need to remove user and put the user of next member in this account
            for member in self.members:
                if member.user_id != self.created_by_id:
                    self.modified_by_id = member.user_id
                    break
            self.created_by = None
            self.created_by_id = None
            self.save()
        else:
            super().reset()

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
"""This manages an Affidavit record in the Auth service."""
from operator import and_

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from auth_api.utils.enums import AffidavitStatus

from .base_model import VersionedModel
from .db import db
from .membership import Membership
from .org import Org
from .user import User


class Affidavit(VersionedModel):
    """This is the model for a Affidavit."""

    __tablename__ = 'affidavits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(60), index=True)
    issuer = Column(String(250))
    status_code = Column(ForeignKey('affidavit_statuses.code'), nullable=False)
    decision_made_by = Column(String(250))
    decision_made_on = Column(DateTime, nullable=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)

    contacts = relationship('ContactLink', primaryjoin='Affidavit.id == ContactLink.affidavit_id', lazy='select')
    status = relationship('AffidavitStatus', foreign_keys=[status_code], lazy='select')
    user = relationship('User', foreign_keys=[user_id], lazy='select')

    @classmethod
    def find_by_org_id(cls, org_id: int, filtered_affidavit_statuses=None):
        """Find an affidavit by org id."""
        if filtered_affidavit_statuses is None:
            filtered_affidavit_statuses = [AffidavitStatus.INACTIVE.value]
        return db.session.query(Affidavit) \
            .join(Membership, Membership.user_id == Affidavit.user_id) \
            .join(Org, Org.id == Membership.org_id) \
            .filter(and_(Org.id == org_id, Affidavit.status_code not in filtered_affidavit_statuses)) \
            .one_or_none()  # There should be only one record at most, else throw error

    @classmethod
    def find_pending_by_user_id(cls, user_id: int):
        """Find pending affidavit by user id."""
        return cls.query.filter_by(user_id=user_id, status_code=AffidavitStatus.PENDING.value).one_or_none()

    @classmethod
    def find_approved_by_user_id(cls, user_id: int):
        """Find pending affidavit by user id."""
        return cls.query.filter_by(user_id=user_id, status_code=AffidavitStatus.APPROVED.value).one_or_none()

    @classmethod
    def find_effective_by_user_guid(cls, user_guid: str, status: str = None):
        """Find pending affidavit by user id."""
        if status:
            affidavit_status = [status]
        else:
            affidavit_status = [AffidavitStatus.PENDING.value, AffidavitStatus.APPROVED.value]
        return db.session.query(Affidavit) \
            .join(User, User.id == Affidavit.user_id) \
            .filter(Affidavit.status_code.in_(affidavit_status)) \
            .filter(User.keycloak_guid == user_guid) \
            .one_or_none()

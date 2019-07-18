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
"""This manages a affiliation record."""

from sqlalchemy import Column, Date, ForeignKey, Integer, text
from sqlalchemy.orm import relationship

from .db import db, ma


class Affiliation(db.Model):
    """Used to hold the affiliation information."""

    __tablename__ = 'affiliation'

    affiliation_id = Column(Integer, primary_key=True, server_default=text("nextval('affiliation_id_seq'::regclass)"))
    affiliation_status_code = Column(ForeignKey('affiliation_status.status_code'), nullable=False)
    business_id = Column(ForeignKey('affiliation_business.business_id'), nullable=False)
    user_id = Column(ForeignKey('users.user_id'), nullable=False)
    effective_start_date = Column(Date, nullable=False)
    effective_end_date = Column(Date)
    created_by_userid = Column(Integer)
    creation_date = Column(Date)
    modified_by_userid = Column(Integer)
    last_access_date = Column(Date)

    affiliation_statu = relationship('AffiliationStatu')
    business = relationship('AffiliationBusines')
    user = relationship('User')

    @classmethod
    def find_by_user_id(cls, user_id):
        """Return the oldest affiliation record for the provided userid."""
        return cls.query.filter_by(userid=user_id).first()

    def save(self):
        """Store affiliation  into the local cache."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete affiliation."""
        db.session.delete(self)
        db.session.commit()


class UserSchema(ma.ModelSchema):
    """Used to manage the default mapping between JSON and Domain model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps all of the Domain fields to a default schema."""

        model = Affiliation

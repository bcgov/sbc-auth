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
"""This manages a affiliation business record.

"""

from sqlalchemy import Column, Integer, String, text

from .db import db, ma


class AffiliationBusiness(db.Model):
    """Used to hold the business information."""
    __tablename__ = 'affiliation_business'

    business_id = Column(Integer, primary_key=True, server_default=text("nextval('business_id_seq'::regclass)"))
    corp_num = Column(String(20))
    corp_type = Column(String(20))

    @classmethod
    def find_by_business_id(cls, business_id):
        """Return the oldest affiliation business record for the provided user_type_code."""
        return cls.query.filter_by(business_id=business_id).first()

    def save(self):
        """Store the business into the local cache."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Cannot delete business records."""
        return self


class UserSchema(ma.ModelSchema):
    """Used to manage the default mapping between JSON and Domain model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps all of the Domain fields to a default schema."""

        model = AffiliationBusiness

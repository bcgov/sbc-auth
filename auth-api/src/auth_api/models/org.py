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

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db import db


class Org(db.Model):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """Model for an Org record.  Associates User (via User Roles) to Entities."""

    __tablename__ = 'org'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    created_by = Column(ForeignKey('user.id'), nullable=False)
    last_modified = Column(DateTime)
    last_modified_by = Column(ForeignKey('user.id'), nullable=False)
    type_code = Column(ForeignKey('org_type.code'), nullable=False)
    status_code = Column(ForeignKey('org_status.code'), nullable=False)
    name = Column(String(250), index=True)
    contact1 = Column(ForeignKey('contact.id'))
    contact2 = Column(ForeignKey('contact.id'))
    preferred_payment = Column(ForeignKey('payment_type.code'), nullable=False)

    contacts = relationship('ContactLink', back_populates='org')

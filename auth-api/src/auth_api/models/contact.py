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
"""This manages an Contact record in the Auth service.

Orgs, and Entities can have multiple contacts, consisting of mailing addresses,
physical addresses, emails, and phone numbers.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_model import VersionedModel


class Contact(VersionedModel):  # pylint: disable=too-few-public-methods
    """This class manages contact information for orgs and entities."""

    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    street = Column('street', String(250), index=True)
    street_additional = Column('street_additional', String(250))
    city = Column('city', String(100))
    region = Column('region', String(100))
    country = Column('country', String(20))
    postal_code = Column('postal_code', String(15))
    delivery_instructions = Column('delivery_instructions', String(4096))
    phone = Column('phone', String(15))
    phone_extension = Column('phone_extension', String(10))
    email = Column('email', String(100))
    # MVP contact has been migrated over to the contact linking table (revised data model)
    entity_id = Column(Integer, ForeignKey('entities.id'), index=True)

    links = relationship('ContactLink', cascade='all, delete-orphan')

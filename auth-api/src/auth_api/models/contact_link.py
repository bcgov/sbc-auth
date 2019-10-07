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
"""This manages links/associations for contact info.

Orgs, Entities, and Users have contact info that must be persisted.
Address and the other data entities have a many-to-many relationship,
which requires this type of linkage to avoid duplication.
"""

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class ContactLink(BaseModel):  # pylint: disable=too-few-public-methods
    """This class manages linkages between contacts and other data entities."""

    __tablename__ = 'contact_link'

    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contact.id'))
    entity_id = Column(Integer, ForeignKey('entity.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    org_id = Column(Integer, ForeignKey('org.id'))

    contact = relationship('Contact', foreign_keys=[contact_id])
    entity = relationship('Entity', back_populates='contacts', foreign_keys=[entity_id])
    user = relationship('User', back_populates='contacts', foreign_keys=[user_id])
    org = relationship('Org', back_populates='contacts', foreign_keys=[org_id])

    @classmethod
    def find_by_entity_id(cls, entity_id):
        """Return the first contact link with the provided entity id."""
        return cls.query.filter_by(entity_id=entity_id).first()

    @classmethod
    def find_by_user_id(cls, user_id):
        """Return the first contact link with the provided user id."""
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def find_by_org_id(cls, org_id):
        """Return the first contact link with the provided org id."""
        return cls.query.filter_by(org_id=org_id).first()

    def has_links(self):
        """Check whether there are any remaining links for this contact."""
        return self.user_id or self.org_id or self.entity_id

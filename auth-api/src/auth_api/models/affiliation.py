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
"""This manages an Affiliation record in the Auth service.

An Affiliation is between an Org and an Entity.
"""

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class Affiliation(BaseModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """This is the model for an Affiliation."""

    __tablename__ = 'affiliation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(ForeignKey('entity.id'), nullable=False)
    org_id = Column(ForeignKey('org.id'), nullable=False)

    entity = relationship('Entity', foreign_keys=[entity_id])
    org = relationship('Org', back_populates='affiliated_entities', foreign_keys=[org_id])

    @classmethod
    def find_affiliation_by_org_and_entity_ids(cls, org_id, entity_id):
        """Return an affiliation for the provided org and entity ids."""
        return cls.query.filter_by(org_id=org_id, entity_id=entity_id).first()

    @classmethod
    def find_affiliation_by_ids(cls, org_id: int, affiliation_id: int):
        """Return the first Affiliation with the provided ids."""
        return cls.query.filter_by(org_id=org_id).filter_by(id=affiliation_id).first()

    @classmethod
    def find_affiliations_by_org_id(cls, org_id: int):
        """Return the affiliations with the provided org id."""
        return cls.query.filter_by(org_id=org_id).all()

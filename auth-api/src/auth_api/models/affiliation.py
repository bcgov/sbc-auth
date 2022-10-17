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
from __future__ import annotations
from typing import List
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base_model import VersionedModel
from .db import db
from .entity import Entity as EntityModel


class Affiliation(VersionedModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """This is the model for an Affiliation."""

    __tablename__ = 'affiliations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(ForeignKey('entities.id'), nullable=False, index=True)
    org_id = Column(ForeignKey('orgs.id'), nullable=False)

    entity = relationship('Entity', foreign_keys=[entity_id], lazy='select')
    org = relationship('Org', foreign_keys=[org_id], lazy='select')

    @classmethod
    def find_affiliation_by_org_and_entity_ids(cls, org_id, entity_id) -> Affiliation:
        """Return an affiliation for the provided org and entity ids."""
        return cls.query.filter_by(org_id=org_id, entity_id=entity_id).one_or_none()

    @classmethod
    def find_affiliations_by_entity_id(cls, entity_id) -> List[Affiliation]:
        """Return affiliations for the provided entity id."""
        return cls.query.filter_by(entity_id=entity_id).all()

    @classmethod
    def find_affiliation_by_ids(cls, org_id: int, affiliation_id: int) -> Affiliation:
        """Return the first Affiliation with the provided ids."""
        return cls.query.filter_by(org_id=org_id).filter_by(id=affiliation_id).one_or_none()

    @classmethod
    def find_affiliations_by_org_id(cls, org_id: int) -> List[Affiliation]:
        """Return the affiliations with the provided org id."""
        return db.session.query(Affiliation).filter(Affiliation.org_id == org_id)\
            .order_by(Affiliation.created.desc()).all()

    @classmethod
    def find_affiliations_by_business_identifier(cls, business_identifier: str):
        """Return the affiliations with the provided business identifier."""
        return cls.query.join(EntityModel).filter(EntityModel.business_identifier == business_identifier).all()

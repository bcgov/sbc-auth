from sqlalchemy import and_, or_
from typing import List
from requests import session
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_model import BaseModel
from .db import db
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from .entity import Entity
from .affiliation import Affiliation as AffiliationModel


class AffiliationMapping(BaseModel):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """This is the Entity model for the Auth service."""

    __tablename__ = "affiliation_mapping"

    id = Column(Integer, primary_key=True)
    business_identifier = Column("identifier_1", String(75), unique=True, nullable=True)  # business identifier
    bootstrap_identifier = Column("identifier_2", String(75), unique=True, nullable=True)  # temp
    nr_identifier = Column("identifier_3", String(75), unique=True, nullable=True)  # NR
    business_identifier_affilation_id = Column(Integer, ForeignKey("affiliations.id"), nullable=True)
    bootstrap_affilation_id = Column(Integer, ForeignKey("affiliations.id"), nullable=True)
    nr_affiliation_id = Column(Integer, ForeignKey("affiliations.id"), nullable=True)

    # Relationships to the Affiliation model with explicit onclause
    business_affiliation = relationship(
        "Affiliation",
        foreign_keys=[business_identifier_affilation_id],
        backref="business_mappings",
        lazy="joined",
        primaryjoin="Affiliation.id == AffiliationMapping.business_identifier_affilation_id",
    )
    bootstrap_affiliation = relationship(
        "Affiliation",
        foreign_keys=[bootstrap_affilation_id],
        backref="bootstrap_mappings",
        lazy="joined",
        primaryjoin="Affiliation.id == AffiliationMapping.bootstrap_affilation_id",
    )
    nr_affiliation = relationship(
        "Affiliation",
        foreign_keys=[nr_affiliation_id],
        backref="nr_mappings",
        lazy="joined",
        primaryjoin="Affiliation.id == AffiliationMapping.nr_affiliation_id",
    )

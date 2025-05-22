from sqlalchemy import Index, and_, or_
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
    business_identifier = Column("business_identifier", String(75), unique=True, nullable=True)  # business identifier
    bootstrap_identifier = Column("bootstrap_identifier", String(75), unique=True, nullable=True)  # temp
    nr_identifier = Column("nr_identifier", String(75), unique=True, nullable=True)  # NR
    business_identifier_affiliation_id = Column(Integer, ForeignKey("affiliations.id"), nullable=True)
    bootstrap_affiliation_id = Column(Integer, ForeignKey("affiliations.id"), nullable=True)
    nr_affiliation_id = Column(Integer, ForeignKey("affiliations.id", ondelete="CASCADE"), nullable=True)

    __table_args__ = (
        Index("ix_business_identifier", "business_identifier"),
        Index("ix_bootstrap_identifier", "bootstrap_identifier"),
        Index("ix_nr_identifier", "nr_identifier"),
    )

    @classmethod
    def find_by_identifier(cls, nr_id: int):
        """Find an Affiliation Mapping instance that matches the provided id."""
        if nr_id is None:
            return None
        return cls.query.filter_by(nr_identifier=nr_id).first()

from sqlalchemy import Column, Integer, String

from .base_model import BaseModel
from .db import db


class EntityMapping(BaseModel):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """This is the Entity model for the Auth service."""

    __tablename__ = "entity_mapping"

    id = Column(Integer, primary_key=True)
    business_identifier = Column("business_identifier", String(75), index=True, unique=True, nullable=True)
    bootstrap_identifier = Column("bootstrap_identifier", String(75), index=True, unique=True, nullable=True)
    nr_identifier = Column("nr_identifier", String(75), index=True, unique=True, nullable=True)

    @classmethod
    def find_by_nr_identifier(cls, nr_identifier: str):
        """Find an Affiliation Mapping instance that matches the provided id."""
        if nr_identifier is None:
            return None
        return cls.query.filter_by(nr_identifier=nr_identifier).first()

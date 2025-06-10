"""Entity Mapping model which enables us to be able to do pagination on affiliations."""

from sqlalchemy import Column, Integer, String

from .db import db


class EntityMapping(db.Model):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """This is the Entity model for the Auth service."""

    __tablename__ = "entity_mapping"

    id = Column(Integer, primary_key=True)
    business_identifier = Column("business_identifier", String(75), index=True, unique=False, nullable=True)
    bootstrap_identifier = Column("bootstrap_identifier", String(75), index=True, unique=False, nullable=True)
    nr_identifier = Column("nr_identifier", String(75), index=True, unique=False, nullable=True)

    def flush(self):
        """Save and flush."""
        db.session.add(self)
        db.session.flush()
        return self

    def save(self):
        """Save and commit."""
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        return self

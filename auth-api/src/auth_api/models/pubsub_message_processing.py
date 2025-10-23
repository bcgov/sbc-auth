"""This model manages pubsub message processing.

NOTE: Only use this when it's not possible to use other indicators to track message processing.
      Currently used by the account-mailer / auth-queue. This prevents duplicates.
"""

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String

from .db import db


class PubSubMessageProcessing(db.Model):
    """PubSub Message Processing for cloud event messages."""

    __tablename__ = "pubsub_message_processing"

    id = Column(Integer, index=True, primary_key=True)
    cloud_event_id = Column(String(250), nullable=False)
    created = Column(DateTime, default=lambda: datetime.now(tz=UTC))
    message_type = Column(String(250), nullable=False)
    processed = Column(DateTime, nullable=True)

    @classmethod
    def find_by_id(cls, identifier: int):
        """Find a pubsub message processing by id."""
        return cls.query.filter_by(id=int(identifier)).one_or_none()

    @classmethod
    def find_by_cloud_event_id_and_type(cls, cloud_event_id, message_type):
        """Find a pubsub message processing for cloud event id and type."""
        return cls.query.filter_by(cloud_event_id=cloud_event_id, message_type=message_type).one_or_none()

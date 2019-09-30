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
"""This manages an Entity record in the Notification service.

The class and schema are both present in this module.
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_model import BaseModel
from .db import db
from .notification_status import NotificationStatus


class Notification(db.Model, BaseModel):  # pylint: disable=too-few-public-methods
    """This is the Entity model for the Notification service."""

    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True)
    recipients = Column(String(2000), nullable=False)
    request_date = Column(DateTime, nullable=False)
    sent_date = Column(DateTime, nullable=True)
    type_code = Column(ForeignKey('notification_type.code'), nullable=False)
    status_code = Column(ForeignKey('notification_status.code'), nullable=False)

    notification_type = relationship('NotificationType')
    notification_status = relationship('NotificationStatus')

    @classmethod
    def create_from_dict(cls, notify_info: dict):
        """Create a new notification from the provided dictionary."""
        if notify_info:
            notification = Notification()
            notification.recipients = notify_info['recipients']
            notification.request_date = notify_info['requestDate']
            notification.type_code = notify_info['notifyType']
            notification.notification_status = NotificationStatus.get_default_status()
            notification.save()
            return notification
        return None

    @classmethod
    def find_by_notification_id(cls, notification_id):
        """Find a Notification instance that matches the provided id."""
        return cls.query.filter_by(id=notification_id).first()

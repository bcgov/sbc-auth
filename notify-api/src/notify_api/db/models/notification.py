# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Notification data model."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from notify_api.core.utils import to_camel
from notify_api.db.database import BASE
from notify_api.db.models.notification_contents import NotificationContentsRequest, NotificationContentsResponse
from notify_api.db.models.notification_status import NotificationStatus
from notify_api.db.models.notification_type import NotificationType


class NotificationModel(BASE):  # pylint: disable=too-few-public-methods
    """This is the Entity model for the Notification service."""
    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True)
    recipients = Column(String(2000), nullable=False)
    request_date = Column(DateTime, nullable=False)
    sent_date = Column(DateTime, nullable=True)
    type_code = Column(ForeignKey('notification_type.code'), nullable=False)
    status_code = Column(ForeignKey('notification_status.code'), nullable=False)

    notify_type = relationship('NotificationTypeModel')
    notify_status = relationship('NotificationStatusModel')
    contents = relationship('NotificationContentsModel', uselist=False)


class NotificationBase(BaseModel):  # pylint: disable=too-few-public-methods
    """Base Notification model."""
    id: int

    class Config:  # pylint: disable=too-few-public-methods
        orm_mode = True


class NotificationRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """Notification model for resquest."""
    recipients: str = ''
    contents: NotificationContentsRequest = None

    class Config:  # pylint: disable=too-few-public-methods
        alias_generator = to_camel


class NotificationUpdate(NotificationBase):  # pylint: disable=too-few-public-methods
    """Notification model for update."""
    id: int
    sent_date: datetime
    notify_status: str = ''

    class Config:  # pylint: disable=too-few-public-methods
        orm_mode = True


class NotificationResponse(NotificationBase):  # pylint: disable=too-few-public-methods
    """Notification model for response."""
    recipients: str = ''
    request_date: Optional[datetime]
    sent_date: Optional[datetime]
    notify_type: NotificationType = None
    notify_status: NotificationStatus = None
    contents: Optional[NotificationContentsResponse] = None

    class Config:  # pylint: disable=too-few-public-methods
        orm_mode = True
        allow_population_by_alias = True
        alias_generator = to_camel


class Notification(NotificationBase):  # pylint: disable=too-few-public-methods
    """Notification model."""
    recipients: str = ''
    request_date: Optional[datetime]
    sent_date: Optional[datetime]
    type_code: str = ''
    status_code: str = ''

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
"""Notification type data model."""
from enum import Enum

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, String

from notify_api.db.database import BASE


class NotificationTypeModel(BASE):  # pylint: disable=too-few-public-methods
    """This is the model for a notification Type record."""
    __tablename__ = 'notification_type'

    code = Column(String(15), primary_key=True, unique=True)
    desc = Column(String(100))
    default = Column(Boolean(), default=False, nullable=False)


class NotificationType(BaseModel):  # pylint: disable=too-few-public-methods
    """This is pydantic model of notification type."""
    code: str = ''
    desc: str = ''

    class Config:  # pylint: disable=too-few-public-methods
        orm_mode = True


class NotificationTypeEnum(str, Enum):  # pylint: disable=too-few-public-methods
    """Notification types."""

    EMAIL = 'EMAIL'
    TEXT = 'TEXT'

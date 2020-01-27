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
"""Notification contents data model."""
from pydantic import BaseModel, validator
from sqlalchemy import Binary, Column, ForeignKey, Integer, String, Text

from notify_api.core.utils import to_camel
from notify_api.db.database import BASE


class NotificationContentsModel(BASE):  # pylint: disable=too-few-public-methods
    """This is the Entity model for the Notification contents."""
    __tablename__ = 'notification_contents'

    id = Column(Integer, primary_key=True)
    subject = Column(String(2000), nullable=False)
    body = Column(Text, nullable=False)
    attachment_name = Column(String(200), nullable=True)
    attachment = Column(Binary, nullable=True)
    notification_id = Column(ForeignKey('notification.id'), nullable=False)


class NotificationContentsBase(BaseModel):  # pylint: disable=too-few-public-methods
    """This is the Entity Base model for the Notification contents."""
    id: int

    class Config:  # pylint: disable=too-few-public-methods
        orm_mode = True


class NotificationContentsRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """This is the Entity Request model for the Notification contents."""
    subject: str = None
    body: str = None
    attachment_name: str = ''
    attachment_bytes: str = ''
    attachment_url: str = ''

    @validator('subject', 'body', always=True)
    def not_empty(cls, v_field):  # pylint: disable=no-self-argument, no-self-use
        """This is a validator that valiate field is not empty."""
        if not v_field:
            raise ValueError('must not empty')
        return v_field

    class Config:  # pylint: disable=too-few-public-methods
        alias_generator = to_camel


class NotificationContentsResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """This is the Entity Response model for the Notification contents."""
    subject: str = ''
    body: str = ''

    class Config:  # pylint: disable=too-few-public-methods
        orm_mode = True


class NotificationContents(NotificationContentsBase):  # pylint: disable=too-few-public-methods
    """This is the Entity Root model for the Notification contents."""
    id: int
    subject: str = ''
    body: str = ''
    notification_id: int

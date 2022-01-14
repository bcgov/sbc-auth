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
"""Notification content data model."""
from typing import ForwardRef, List, Optional  # noqa: F401 # pylint: disable=unused-import

from pydantic import BaseModel, validator
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from notify_api.core.utils import to_camel
from notify_api.db.database import BASE
from notify_api.db.models.attachment import (  # noqa: F401 # pylint: disable=unused-import
    AttachmentRequest, AttachmentResponse)


ListAttachmentRequest = ForwardRef('List[AttachmentRequest]')
ListAttachmentResponse = ForwardRef('List[AttachmentResponse]')


class ContentModel(BASE):  # pylint: disable=too-few-public-methods
    """This is the Entity model for the Notification content."""

    __tablename__ = 'content'

    id = Column(Integer, primary_key=True)
    subject = Column(String(2000), nullable=False)
    body = Column(Text, nullable=False)
    notification_id = Column(ForeignKey('notification.id'), nullable=False)

    attachments = relationship('AttachmentModel', uselist=True, order_by='AttachmentModel.attach_order')


class ContentBase(BaseModel):  # pylint: disable=too-few-public-methods
    """This is the Entity Base model for the Notification content."""

    id: int

    class Config:  # pylint: disable=too-few-public-methods
        """Config."""

        orm_mode = True


class ContentRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """Entity Request model for the Notification content."""

    subject: str = None
    body: str = None
    attachments: Optional[ListAttachmentRequest] = None

    @validator('subject', 'body', always=True)
    def not_empty(cls, v_field):  # pylint: disable=no-self-argument, no-self-use # noqa: N805
        """Valiate field is not empty."""
        if not v_field:
            raise ValueError('must not empty')
        return v_field

    class Config:  # pylint: disable=too-few-public-methods
        """Config."""

        alias_generator = to_camel


class ContentResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """This is the Entity Response model for the Notification content."""

    subject: str = ''
    body: str = ''
    attachments: Optional[ListAttachmentResponse] = None

    class Config:  # pylint: disable=too-few-public-methods
        """Config."""

        orm_mode = True


class ContentUpdate(ContentBase):  # pylint: disable=too-few-public-methods
    """Content model for update."""

    id: int
    subject: str = ''
    body: str = ''

    class Config:  # pylint: disable=too-few-public-methods
        """Config."""

        orm_mode = True


class Content(ContentBase):  # pylint: disable=too-few-public-methods
    """This is the Entity Root model for the Notification content."""

    id: int
    subject: str = ''
    body: str = ''
    notification_id: int

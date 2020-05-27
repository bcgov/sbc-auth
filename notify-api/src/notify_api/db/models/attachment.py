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
from sqlalchemy import Binary, Column, ForeignKey, Integer, String

from notify_api.core.utils import to_camel
from notify_api.db.database import BASE


class AttachmentModel(BASE):  # pylint: disable=too-few-public-methods
    """This is the Entity model for the Notification contents attachment."""

    __tablename__ = 'attachment'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(200), nullable=False)
    file_bytes = Column(Binary, nullable=False)
    attach_order = Column(Integer, nullable=True)
    content_id = Column(ForeignKey('content.id'), nullable=False)


class AttachmentBase(BaseModel):  # pylint: disable=too-few-public-methods
    """This is the Entity Base model for the Notification attachment."""

    id: int

    class Config:  # pylint: disable=too-few-public-methods
        """Config."""

        orm_mode = True


class AttachmentRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """This is the Entity Request model for the Notification attachment."""

    file_name: str = None
    file_bytes: str = None
    file_url: str = None
    attach_order: str = None

    @validator('file_name', always=True)
    def not_empty(cls, v_field):  # pylint: disable=no-self-argument, no-self-use # noqa: N805
        """Valiate field is not empty."""
        if not v_field:
            raise ValueError('must not empty')
        return v_field

    @validator('attach_order')
    def must_contain_one(cls,           # noqa: N805
                         v_field,
                         values,
                         **kwargs):     # pylint: disable=no-self-use, no-self-argument, unused-argument
        """Valiate field is not empty."""
        if 'file_bytes' not in values and 'file_url' not in values:
            raise ValueError('file content must input')
        return v_field

    class Config:  # pylint: disable=too-few-public-methods
        """Config."""

        alias_generator = to_camel


class AttachmentResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """This is the Entity Response model for the Notification attachment."""

    file_name: str = None
    attach_order: str = None

    class Config:  # pylint: disable=too-few-public-methods
        """Config."""

        orm_mode = True


class Attachment(AttachmentBase):  # pylint: disable=too-few-public-methods
    """This is the Entity Root model for the Notification attachment."""

    id: int
    content_id: int

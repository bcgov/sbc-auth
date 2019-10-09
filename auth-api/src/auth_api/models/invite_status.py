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
"""This manages a Invitation Status record.

It defines the different statuses of an Invitation.
"""

from sqlalchemy import Boolean, Column, String

from .base_model import BaseModel


class InvitationStatus(BaseModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """This is the Invitation Status model for the Auth service."""

    __tablename__ = 'invitation_status'

    code = Column(String(15), primary_key=True)
    desc = Column(String(100))
    default = Column(Boolean(), default=False, nullable=False)

    @classmethod
    def get_default_status(cls):
        """Return the default status code for an Invitation."""
        return cls.query.filter_by(default=True).first()

    @classmethod
    def get_status_by_code(cls, code: str):
        """Return the status object corresponding to the given code."""
        return cls.query.filter_by(code=code).first()

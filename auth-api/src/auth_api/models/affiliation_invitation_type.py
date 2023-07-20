# Copyright © 2023 Province of British Columbia
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
"""This manages an Affiliation Invitation Type record.

It defines the different types of an Affiliation Invitation.
"""

from .base_model import BaseCodeModel


class AffiliationInvitationType(BaseCodeModel):  # pylint: disable=too-few-public-methods
    """This is the Affiliation Invitation Type model for the Auth service."""

    __tablename__ = 'affiliation_invitation_types'

    @classmethod
    def get_default_type(cls):
        """Return the default type code for an Affiliation Invitation."""
        return cls.query.filter_by(default=True).first()

    @classmethod
    def get_type_by_code(cls, code: str):
        """Return the type object corresponding to the given code."""
        return cls.query.filter_by(code=code).first()

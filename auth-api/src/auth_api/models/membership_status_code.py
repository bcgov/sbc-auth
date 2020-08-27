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
"""This manages a Membership Type record.

It defines the available types of membership Status have with Orgs.
"""

from sqlalchemy import Column, Integer, String

from .base_model import BaseModel


class MembershipStatusCode(BaseModel):  # pylint: disable=too-few-public-methods
    """This is the Membership Status model for the Auth service."""

    __tablename__ = 'membership_status_code'

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(25))
    description = Column(String(100))

    @classmethod
    def get_membership_status_by_code(cls, name):
        """Return the membership type object that corresponds to given code."""
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_default_type(cls):
        """Return the default type code for Membership Status."""
        return 1

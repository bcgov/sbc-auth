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
"""This model manages a Membership item in the Auth Service.

The Membership object connects User models to one or more Org models.
"""

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base_model import BaseModel
from .membership_type import MembershipType


class Membership(BaseModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """Model for a Membership model.  Associates Users and Orgs."""

    __tablename__ = 'membership'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    org_id = Column(ForeignKey('org.id'), nullable=False)
    membership_type_code = Column(
        ForeignKey('membership_type.code'), nullable=False
    )

    membership_type = relationship('MembershipType', foreign_keys=[membership_type_code])
    user = relationship('User', back_populates='orgs', foreign_keys=[user_id])
    org = relationship('Org', back_populates='members', foreign_keys=[org_id])

    def __init__(self, **kwargs):
        """Initialize a new membership."""
        self.org_id = kwargs.get('org_id')
        self.user_id = kwargs.get('user_id')

        self.membership_type_code = kwargs.get('membership_type_code')
        if self.membership_type_code is None:
            self.membership_type = MembershipType.get_default_type()

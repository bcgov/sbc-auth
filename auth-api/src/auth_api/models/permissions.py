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

from sqlalchemy import Column, Integer, String

from .base_model import BaseModel


class Permissions(BaseModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """Model for a Permissions model.  Associates Roles and Actions."""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    membership_type_code = Column(String(25), nullable=True)
    org_status_code = Column(String(25), nullable=True)
    actions = Column(String(100), primary_key=True, autoincrement=False)

    @classmethod
    def get_permissions_by_membership(cls, org_status_code: str, membership_type: str):
        """Find the first membership with the given id and return it."""
        return cls.query.filter_by(membership_type_code=membership_type, org_status_code=org_status_code).all()

    @classmethod
    def get_all_permissions(cls):
        """Find the first membership with the given id and return it."""
        return cls.query.all()

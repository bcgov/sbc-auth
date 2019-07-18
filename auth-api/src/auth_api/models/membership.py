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

from sqlalchemy import Column, DateTime, Integer, ForeignKey

from .db import db, ma


class Membership(db.Model):
    """Model for a Membership model.  Associates Users and Orgs."""

    __tablename__ = "membership"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    user = Column(ForeignKey("user.id"), nullable=False)
    org = Column(ForeignKey("org.id"), nullable=False)
    membership_type_code = Column(
        ForeignKey("membership_type.membership_type_code"), nullable=False
    )


class MembershipSchema(ma.ModelSchema):
    """Used to manage the default mapping betweeen JSON and Membership model."""

    class Meta:
        """Maps all of the Membership fields to a default schema."""

        model = Membership

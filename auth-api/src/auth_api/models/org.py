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
"""This manages an Org record, where an Org associates a User (via a Role) with one or more Entities.

Basic users will have an internal Org that is not created explicitly, but implicitly upon User account creation.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from .db import db, ma

class Org(db.Model):
    """Model for an Org record.  Associates User (via User Roles) to Entities."""

    __tablename__ = "org"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    created_by = Column(ForeignKey('user.id'), nullable=False)
    last_modified = Column(DateTime)
    last_modified_by = Column(ForeignKey('user.id'), nullable=False)
    org_type_code = Column(ForeignKey('org_type.org_type_code'), nullable=False)
    org_status_code = Column(ForeignKey('org_status.org_status_code'), nullable=False)
    org_name = Column(String(250), index=True)
    org_address = Column(String(250), index=True)
    org_preferred_pay_code = Column(ForeignKey('preferred_pay_types.type_id'), nullable=False)

class OrgSchema(ma.ModelSchema):
    """Used to manage the default mapping between JSON and Org model."""

    class Meta:
        """Maps all of the Org fields to a default schema."""

        model = Org

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
"""This manages an Affiliation record in the Auth service.

An Affiliation is between an Org and an Entity.
"""

from sqlalchemy import Column, DateTime, Integer, ForeignKey

from .db import db, ma


class Affiliation(db.Model):
    """This is the model for an Affiliation."""

    __tablename__ = "affiliation"

    id = Column(Integer, primary_key=True)
    entity_id = Column(ForeignKey("entity.entity_id"), nullable=False)
    org_id = Column(ForeignKey("org.org_id"), nullable=False)
    created = Column(DateTime)
    created_by = Column(ForeignKey("user.id"), nullable=False)


class AffiliationSchema(ma.ModelSchema):
    """This is the Schema for an Affiliation model.  It is used to managed
    the default mapping between the JSON and model."""

    class Meta:
        """Maps all of the Affiliation fields to a default schema."""

        model = Affiliation

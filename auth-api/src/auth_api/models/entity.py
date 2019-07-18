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
"""This manages an Entity record in the Auth service.

The class and schema are both present in this module.
"""

from sqlalchemy import Column, Integer

from .db import db, ma


class Entity(db.Model):
    """This is the Entity model for the Auth service."""

    __tablename__ = "entity"

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, unique=True, nullable=False)


class EntitySchema(ma.ModelSchema):
    """Used to manage the default mapping between JSON and the Entity model."""

    class Meta:
        """Maps all of the Entity fields to a default schema."""

        model = Entity

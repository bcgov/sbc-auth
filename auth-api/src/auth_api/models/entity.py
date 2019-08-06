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

from marshmallow import fields
from sqlalchemy import Column, Integer, String

from .base_model import BaseModel
from .base_schema import BaseSchema
from .contact import ContactSchema
from .db import db


class Entity(db.Model, BaseModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """This is the Entity model for the Auth service."""

    __tablename__ = 'entity'

    id = Column(Integer, primary_key=True)
    business_identifier = Column('business_identifier', String(75), unique=True, nullable=False)
    contacts = db.relationship('Contact')

    @classmethod
    def find_by_business_identifier(cls, business_identifier):
        """Return the first entity with the provided business identifier."""
        return cls.query.filter_by(business_identifier=business_identifier).first()


class EntitySchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """Used to manage the default mapping between JSON and the Entity model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps all of the Entity fields to a default schema."""

        model = Entity

    business_identifier = fields.String(data_key='businessIdentifier')
    contacts = fields.Nested(ContactSchema, many=True)

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

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class Entity(BaseModel):  # pylint: disable=too-few-public-methods
    """This is the Entity model for the Auth service."""

    __tablename__ = 'entity'

    id = Column(Integer, primary_key=True)
    business_identifier = Column('business_identifier', String(75), unique=True, nullable=False)
    pass_code = Column('pass_code', String(75), unique=False, nullable=True)
    contacts = relationship('ContactLink', back_populates='entity')

    @classmethod
    def find_by_business_identifier(cls, business_identifier):
        """Return the first entity with the provided business identifier."""
        return cls.query.filter_by(business_identifier=business_identifier).first()

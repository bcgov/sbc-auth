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

from flask import current_app
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from auth_api.utils.passcode import passcode_hash
from auth_api.utils.util import camelback2snake
from .base_model import BaseModel


class Entity(BaseModel):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """This is the Entity model for the Auth service."""

    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True)
    business_identifier = Column('business_identifier', String(75), unique=True, nullable=False)
    pass_code = Column('pass_code', String(75), unique=False, nullable=True)
    pass_code_claimed = Column('pass_code_claimed', Boolean(), default=False)
    business_number = Column('business_number', String(100), nullable=True)
    name = Column('name', String(250), nullable=True)
    corp_type_code = Column(String(15), ForeignKey('corp_types.code'), nullable=False)
    corp_sub_type_code = Column(String(15), ForeignKey('corp_types.code'))
    folio_number = Column('folio_number', String(50), nullable=True, index=True)
    status = Column(String(), nullable=True)
    last_modified_by = Column(String(), nullable=True)
    last_modified = Column(DateTime, default=None, nullable=True)

    contacts = relationship('ContactLink', back_populates='entity')
    corp_type = relationship('CorpType', foreign_keys=[corp_type_code], lazy='joined', innerjoin=True)
    corp_sub_type = relationship('CorpType', foreign_keys=[corp_sub_type_code])
    affiliations = relationship('Affiliation', cascade='all,delete,delete-orphan', lazy='joined')

    @classmethod
    def find_by_business_identifier(cls, business_identifier):
        """Return the first entity with the provided business identifier."""
        return cls.query.filter_by(business_identifier=business_identifier).one_or_none()

    @classmethod
    def create_from_dict(cls, entity_info: dict):
        """Create a new Entity from the provided dictionary."""
        if entity_info:
            entity = Entity(**camelback2snake(entity_info))
            entity.pass_code = passcode_hash(entity.pass_code)
            current_app.logger.debug(f'Creating entity from dictionary {entity_info}')
            entity.save()
            return entity
        return None

    @classmethod
    def find_by_entity_id(cls, entity_id):
        """Find an Entity instance that matches the provided id."""
        return cls.query.filter_by(id=entity_id).first()

    def reset(self):
        """Reset an Entity back to init state."""
        self.pass_code_claimed = False
        self.folio_number = None
        self.name = 'Test ' + self.business_identifier + ' Name'
        self.created_by_id = None
        self.created = None
        self.modified_by_id = None
        self.modified = None
        self.save()

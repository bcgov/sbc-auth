# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Service for managing Entity data."""

from typing import Any, Dict

from sbc_common_components.tracing.service_tracing import ServiceTracing

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.contact import Contact as ContactModel
from auth_api.models.entity import Entity as EntityModel
from auth_api.models.entity import EntitySchema


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Entity:
    """Manages all aspect of Entity data.

    This manages updating, retrieving, and creating Entity data via the Entity model.
    """

    def __init__(self, model):
        """Return an Entity Service."""
        self._model = model

    @property
    def business_identifier(self):
        """Return the business identifier for this Entity."""
        return self._model.business_identifier

    @business_identifier.setter
    def business_identifier(self, value: str):
        """Set the business identifier for this Entity."""
        self._model.business_identifier = value

    @property
    def contact1(self):
        """Return the first contact for this Entity."""
        return self._model.contact1

    @contact1.setter
    def contact1(self, value: str):
        """Set the first contact for this Entity."""
        self._model.contact1 = value

    @property
    def contact2(self):
        """Return the second contact for this Entity."""
        return self._model.contact2

    @contact2.setter
    def contact2(self, value: str):
        """Set the second contact for this Entity."""
        self._model.contact2 = value

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the entity as a python dictionary.

        None fields are not included in the dictionary.
        """
        entity_schema = EntitySchema()
        obj = entity_schema.dump(self._model, many=False)
        return obj

    @classmethod
    def find_by_business_identifier(cls, business_identifier: str = None):
        """Given a business identifier, this will return the corresponding entity or None."""
        if not business_identifier:
            return None

        entity_model = EntityModel.find_by_business_identifier(business_identifier)

        if not entity_model:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = Entity(entity_model)
        return entity

    @staticmethod
    def __save_contact(contact):
        """Create and persist contact information in database."""
        if contact is None:
            return None

        contact_model = ContactModel()
        # TODO: This needs to be done in a better way and include other contact fields (post MVP)
        contact_model.email = contact.get('emailAddress', None)
        contact_model.phone = contact.get('phoneNumber', None)
        contact_model.phone_extension = contact.get('extension', None)
        contact_model = contact_model.flush()
        return contact_model

    @staticmethod
    def __update_contact(contact, contact_info):
        """Update and persist contact information in the database."""
        if contact is None or contact_info is None:
            return None

        # TODO: This needs to be done in a better way and include other contact fields (post MVP)
        contact.email = contact_info.get('emailAddress', None)
        contact.phone = contact_info.get('phoneNumber', None)
        contact.phone_extension = contact_info.get('extension', None)
        contact = contact.flush()
        return contact

    @staticmethod
    def create_entity(entity_info: Dict[str, Any]):
        """Create an Entity."""
        entity = EntityModel()
        entity.business_identifier = entity_info.get('businessIdentifier', None)
        entity.contact1 = entity_info.get('contact1', None)
        entity.contact2 = entity_info.get('contact2', None)

        # persist contact info
        entity.contact1 = Entity.__save_contact(entity.contact1)
        entity.contact2 = Entity.__save_contact(entity.contact2)

        entity = entity.flush()
        entity.commit()
        return Entity(entity)

    @staticmethod
    def update_entity(business_identifier, entity_info: Dict[str, Any]):
        """Update an Entity."""
        business_identifier = entity_info.get('businessIdentifier', None)
        contact1 = entity_info.get('contact1', None)
        contact2 = entity_info.get('contact2', None)

        entity = EntityModel.find_by_business_identifier(business_identifier)

        # update contact info, or create if not already set
        if entity.contact1 is not None:
            entity.contact1 = Entity.__update_contact(entity.contact1, contact1)
        else:
            entity.contact1 = Entity.__save_contact(contact1)

        if entity.contact2 is not None:
            entity.contact2 = Entity.__update_contact(entity.contact2, contact2)
        else:
            entity.contact2 = Entity.__save_contact(contact2)

        entity = entity.flush()
        entity.commit()
        return Entity(entity)

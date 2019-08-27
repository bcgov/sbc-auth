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

from sbc_common_components.tracing.service_tracing import ServiceTracing

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models.entity import Entity as EntityModel
from auth_api.schemas import EntitySchema
from auth_api.utils.util import camelback2snake


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Entity:
    """Manages all aspect of Entity data.

    This manages updating, retrieving, and creating Entity data via the Entity model.
    """

    def __init__(self, model):
        """Return an Entity Service."""
        self._model = model

    @property
    def identifier(self):
        """Return the unique identifier for this entity."""
        return self._model.id

    @property
    def pass_code(self):
        """Return the pass_code for this entity."""
        return self._model.pass_code

    def set_pass_code_claimed(self, pass_code_claimed):
        """Set the pass_code_claimed status."""
        self._model.pass_code_claimed = pass_code_claimed
        self._model.save()

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
            return None

        entity = Entity(entity_model)
        return entity

    @staticmethod
    def find_by_entity_id(entity_id):
        """Find and return an existing Entity with the provided id."""
        if entity_id is None:
            return None

        entity_model = EntityModel.find_by_entity_id(entity_id)
        if not entity_model:
            return None

        return Entity(entity_model)

    @staticmethod
    def create_entity(entity_info: dict):
        """Create an Entity."""
        entity = EntityModel.create_from_dict(entity_info)
        entity.commit()
        return Entity(entity)

    def add_contact(self, contact_info: dict):
        """Add a business contact to this entity."""
        # check for existing contact (we only want one contact per user)
        contact_link = ContactLinkModel.find_by_entity_id(self._model.id)
        if contact_link is not None:
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        contact = ContactModel(**camelback2snake(contact_info))
        contact.commit()

        contact_link = ContactLinkModel()
        contact_link.contact = contact
        contact_link.entity = self._model
        contact_link.commit()

        return self

    def update_contact(self, contact_info: dict):
        """Update a business contact for this entity."""
        # find the contact link object for this entity
        contact_link = ContactLinkModel.find_by_entity_id(self._model.id)
        if contact_link is None or contact_link.contact is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        contact = contact_link.contact
        contact.update_from_dict(**camelback2snake(contact_info))
        contact.commit()

        return self

    def delete_contact(self):
        """Delete a business contact for this entity."""
        contact_link = ContactLinkModel.find_by_entity_id(self._model.id)
        if contact_link is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        del contact_link.entity
        contact_link.commit()

        if not contact_link.has_links():
            contact = contact_link.contact
            contact_link.delete()
            contact.delete()

        return self

    def get_contact(self):
        """Get the contact for this business."""
        contact_link = ContactLinkModel.find_by_entity_id(self._model.id)
        if contact_link is None:
            return None
        return contact_link.contact

    def validate_pass_code(self, pass_code):
        """Get the contact for the given entity."""
        if pass_code == self._model.pass_code:
            return True
        return False

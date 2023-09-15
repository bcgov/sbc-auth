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

import secrets
import string
from typing import Tuple

from flask import current_app
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models.entity import Entity as EntityModel
from auth_api.schemas import EntitySchema
from auth_api.utils.account_mailer import publish_to_mailer
from auth_api.utils.passcode import passcode_hash
from auth_api.utils.roles import ALL_ALLOWED_ROLES
from auth_api.utils.user_context import UserContext, user_context
from auth_api.utils.util import camelback2snake
from .authorization import check_auth


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
    def business_identifier(self):
        """Return the business identifier for this entity."""
        return self._model.business_identifier

    @property
    def name(self):
        """Return the business identifier for this entity."""
        return self._model.name

    @property
    def pass_code(self):
        """Return the pass_code for this entity."""
        return self._model.pass_code

    @property
    def corp_type(self):
        """Return the corp_type_code for this entity."""
        return self._model.corp_type_code

    @property
    def pass_code_claimed(self):
        """Return the pass_code_claimed for this entity."""
        return self._model.pass_code_claimed

    @property
    def status(self):
        """Return the status for this entity."""
        return self._model.status

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
    def find_by_business_identifier(cls, business_identifier: str = None,
                                    allowed_roles: Tuple = None, skip_auth: bool = False):
        """Given a business identifier, this will return the corresponding entity or None."""
        if not business_identifier:
            return None
        entity_model = EntityModel.find_by_business_identifier(business_identifier)

        if not entity_model:
            return None

        if not skip_auth:
            check_auth(one_of_roles=allowed_roles, business_identifier=business_identifier)

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
    def save_entity(entity_info: dict):
        """Create/update an entity from the given dictionary."""
        if not entity_info:
            return None

        existing_entity = EntityModel.find_by_business_identifier(entity_info['businessIdentifier'])
        if existing_entity is None:
            entity_model = EntityModel.create_from_dict(entity_info)
        else:
            # TODO temporary allow update passcode, should replace with reset passcode endpoint.
            entity_info['passCode'] = passcode_hash(entity_info['passCode'])
            existing_entity.update_from_dict(**camelback2snake(entity_info))
            entity_model = existing_entity
            entity_model.commit()

        entity = Entity(entity_model)
        return entity

    @staticmethod
    @user_context
    def update_entity(business_identifier: str, entity_info: dict, **kwargs):
        """Update an entity from the given dictionary.

        Completely replaces the entity including the business identifier
        """
        if not entity_info or not business_identifier:
            return None
        user_from_context: UserContext = kwargs['user_context']
        if not user_from_context.is_system():
            check_auth(one_of_roles=ALL_ALLOWED_ROLES, business_identifier=business_identifier)
        entity = EntityModel.find_by_business_identifier(business_identifier)
        if entity is None or entity.corp_type_code is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if user_from_context.is_system():
            if entity_info.get('passCode') is not None:
                entity_info['passCode'] = passcode_hash(entity_info['passCode'])

        # Small mapping from state -> status. EX in LEAR: Business.State.HISTORICAL
        if 'state' in entity_info:
            entity_info['status'] = entity_info['state']
            del entity_info['state']

        entity.update_from_dict(**camelback2snake(entity_info))
        entity.commit()

        entity = Entity(entity)
        return entity

    @staticmethod
    @user_context
    def reset_passcode(business_identifier: str, email_addresses: str = None, **kwargs):
        """Reset the entity passcode and send email."""
        user_from_context: UserContext = kwargs['user_context']
        check_auth(one_of_roles=ALL_ALLOWED_ROLES, business_identifier=business_identifier)
        current_app.logger.debug('reset passcode')
        entity: EntityModel = EntityModel.find_by_business_identifier(business_identifier)
        # generate passcode and set
        new_pass_code = ''.join(secrets.choice(string.digits) for i in range(9))

        entity.pass_code = passcode_hash(new_pass_code)
        entity.pass_code_claimed = False
        entity.save()
        if email_addresses:
            mailer_payload = {
                'emailAddresses': email_addresses,
                'passCode': new_pass_code,
                'businessIdentifier': business_identifier,
                'businessName': entity.name,
                'isStaffInitiated': user_from_context.is_staff()
            }
            publish_to_mailer(
                notification_type='resetPasscode', business_identifier=business_identifier, data=mailer_payload
            )

        entity = Entity(entity)
        return entity

    def add_contact(self, contact_info: dict):
        """Add a business contact to this entity."""
        # check for existing contact (we only want one contact per user)
        contact_link = ContactLinkModel.find_by_entity_id(self._model.id)
        if contact_link is not None:
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        contact = ContactModel(**camelback2snake(contact_info))
        contact.flush()

        contact_link = ContactLinkModel()
        contact_link.contact = contact
        contact_link.entity = self._model
        contact_link.save()

        return self

    def update_contact(self, contact_info: dict):
        """Update a business contact for this entity."""
        # find the contact link object for this entity
        contact_link = ContactLinkModel.find_by_entity_id(self._model.id)
        if contact_link is None or contact_link.contact is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        contact = contact_link.contact
        contact.update_from_dict(**camelback2snake(contact_info))
        contact.save()

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

    def get_contact(self) -> ContactModel:
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

    def delete(self):
        """Delete an entity."""
        if self._model is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if self._model.affiliations:
            raise BusinessException(Error.ENTITY_DELETE_FAILED, None)

        if self._model.contacts:
            self.delete_contact()

        self._model.delete()

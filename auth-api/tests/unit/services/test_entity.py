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
"""Tests for the Entity service.

Test suite to ensure that the Entity service routines are working as expected.
"""

from auth_api.models.entity import Entity as EntityModel
from auth_api.services.entity import Entity as EntityService


def test_as_dict():
    """Assert that the Entity is exported correctly as a dictionary."""
    entity_model = EntityModel(business_identifier='CP1234567')
    entity = EntityService(entity_model)

    assert entity.as_dict() == {
        'businessIdentifier': 'CP1234567'
    }


def test_create_entity(app, session):  # pylint:disable=unused-argument
    """Assert that an Entity can be created."""
    entity_info = {
        'businessIdentifier': 'CP1234567'
    }

    with app.app_context():
        entity = EntityService.create_entity(entity_info)

        assert entity is not None


def test_add_contact(app, session):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an Entity."""
    entity_info = {
        'businessIdentifier': 'CP1234567'
    }

    with app.app_context():
        entity = EntityService.create_entity(entity_info)
        contact_info = {
            'emailAddress': 'foo@bar.com'
        }
        updated_entity = EntityService.add_contact(entity.business_identifier, contact_info)

        assert updated_entity is not None

        contact = EntityService.get_contact_for_business(updated_entity.business_identifier)

        assert contact is not None
        assert contact.email == 'foo@bar.com'


def test_update_contact(app, session):  # pylint:disable=unused-argument
    """Assert that a contact for an entity can be updated."""
    entity_info = {
        'businessIdentifier': 'CP1234567'
    }

    with app.app_context():
        entity = EntityService.create_entity(entity_info)
        contact_info = {
            'emailAddress': 'foo@bar.com'
        }
        EntityService.add_contact(entity.business_identifier, contact_info)

        contact_info['phoneNumber'] = '(555)-555-5555'
        updated_entity = EntityService.update_contact(entity.business_identifier, contact_info)

        assert updated_entity

        updated_contact = EntityService.get_contact_for_business(updated_entity.business_identifier)

        assert updated_contact is not None
        assert updated_contact.phone == '(555)-555-5555'

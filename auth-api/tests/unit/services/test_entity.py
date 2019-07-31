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

from auth_api.models.contact import Contact as ContactModel
from auth_api.models.entity import Entity as EntityModel
from auth_api.services.entity import Entity as EntityService


def test_as_dict():
    """Assert that the Entity is exported correctly as a dictionary."""
    contact_model = ContactModel(phone='111-222-3333', phone_extension='123', email='abc123@mail.com')
    entity_model = EntityModel(business_identifier='CP1234567', contact1=contact_model)
    entity = EntityService(entity_model)

    assert entity.as_dict() == {
        'business_identifier': 'CP1234567',
        'contact1': {
            'phone': '111-222-3333',
            'phone_extension': '123',
            'email': 'abc123@mail.com'
        }
    }


def test_create_entity(app, session):  # pylint:disable=unused-argument
    """Assert that an Entity can be created."""
    entity_info = {
        'business_identifier': 'CP1234567',
        'contact1': {
            'phone': '111-222-3333',
            'phone_extension': '123',
            'email': 'abc123@mail.com'
        }
    }

    with app.app_context():
        entity = EntityService.create_entity(entity_info)

        assert entity is not None


def test_update_entity(app, session):  # pylint:disable=unused-argument
    """Assert that an Entity can be updated."""
    entity_info = {
        'business_identifier': 'CP1234567',
        'contact1': {
            'phone': '111-222-3333',
            'phone_extension': '123',
            'email': 'abc123@mail.com'
        }
    }

    with app.app_context():
        entity = EntityService.create_entity(entity_info)
        entity_info['contact2'] = {
            'street': '123 Roundabout Way'
        }
        entity = EntityService.update_entity('CP1234567', entity_info)

        assert entity.contact2 is not None
        assert entity.contact2.street == '123 Roundabout Way'

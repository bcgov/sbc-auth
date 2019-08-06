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
"""Tests for the Contact model.

Test suite to ensure that the Contact model routines are working as expected.
"""

from auth_api.models import Contact as ContactModel
from auth_api.models import Entity as EntityModel


def test_contact(session):
    """Assert that a Contact can be stored in the service."""
    entity = EntityModel(business_identifier='CP1234567')
    session.add(entity)

    contact = ContactModel(
        street='123 Roundabout Lane',
        street_additional='Unit 1',
        city='Victoria',
        region='British Columbia',
        country='CA',
        postal_code='V1A 1A1',
        delivery_instructions='Ring buzzer 123',
        phone='111-222-3333',
        phone_extension='123',
        email='abc123@mail.com',
        entity_id=entity.id
    )

    session.add(contact)
    session.commit()
    assert contact.id is not None

def test_find_by_entity_id(session):
    """Assert that a Contact can be retrieved via the entity id."""
    entity = EntityModel(business_identifier='CP1234567')
    session.add(entity)

    contact = ContactModel(
        entity_id=entity.id
    )

    session.add(contact)

    result_contact = ContactModel.find_by_entity_id(entity_id=entity.id)

    assert result_contact is not None

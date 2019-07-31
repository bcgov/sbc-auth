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
"""Tests for the Entity model.

Test suite to ensure that the Entity model routines are working as expected.
"""

from auth_api.models import Contact as ContactModel
from auth_api.models import Entity as EntityModel


def test_entity(session):
    """Assert that an Entity can be stored in the service."""
    contact = ContactModel(email='abc123@email.com', phone='3334445555', phone_extension='123')
    entity = EntityModel(business_identifier='CP1234567', contact1=contact)
    session.add(contact)
    session.add(entity)
    session.commit()
    assert entity.id is not None


def test_entity_find_by_business_id(session):
    """Assert that an Entity can be retrieved via business identifier."""
    entity = EntityModel(business_identifier='CP1234567')
    session.add(entity)
    session.commit()

    business_id = 'CP1234567'

    result_entity = EntityModel.find_by_business_identifier(business_identifier=business_id)

    assert result_entity.id is not None

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

from auth_api.models import Entity as EntityModel


def test_entity(session):
    """Assert that an Entity can be stored in the service."""
    entity = EntityModel(business_identifier='CP1234567', business_number='791861073BC0001', name='Foobar, Inc.')
    session.add(entity)
    session.commit()
    assert entity.id is not None


def test_entity_find_by_business_id(session):
    """Assert that an Entity can be retrieved via business identifier."""
    entity = EntityModel(business_identifier='CP1234567', business_number='791861073BC0001', name='Foobar, Inc.')
    session.add(entity)
    session.commit()

    business_id = 'CP1234567'

    result_entity = EntityModel.find_by_business_identifier(business_identifier=business_id)

    assert result_entity.id is not None


def test_create_from_dict(session):  # pylint:disable=unused-argument
    """Assert that an Entity can be created from schema."""
    updated_entity_info = {
        'businessIdentifier': 'CP1234567',
        'businessNumber': '791861073BC0001',
        'passCode': '9898989',
        'name': 'Barfoo, Inc.'
    }

    result_entity = EntityModel.create_from_dict(updated_entity_info)

    assert result_entity.id is not None


def test_create_from_dict_no_schema(session):  # pylint:disable=unused-argument
    """Assert that an Entity can not be created without schema."""
    result_entity = EntityModel.create_from_dict(None)

    assert result_entity is None

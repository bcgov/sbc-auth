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

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.entity import Entity as EntityModel
from auth_api.services.entity import Entity as EntityService


TEST_CONTACT_INFO = {
    'email': 'foo@bar.com'
}

TEST_UPDATED_CONTACT_INFO = {
    'email': 'bar@foo.com'
}


def factory_entity_model(business_identifier='CP1234567',
                         business_number='791861073BC0001',
                         name='Foobar, Inc.', pass_code=None):
    """Return a valid entity object with the provided fields."""
    entity = EntityModel(business_identifier=business_identifier,
                         business_number=business_number,
                         name=name,
                         pass_code=pass_code)
    entity.save()
    return entity


def test_as_dict(session):  # pylint:disable=unused-argument
    """Assert that the Entity is exported correctly as a dictionary."""
    entity_model = factory_entity_model(business_identifier='CP1234567')
    entity = EntityService(entity_model)

    dictionary = entity.as_dict()
    assert dictionary['businessIdentifier'] == 'CP1234567'


def test_create_entity(session):  # pylint:disable=unused-argument
    """Assert that an Entity can be created from a dictionary."""
    entity = EntityService.create_entity({
        'businessIdentifier': 'CP1234567',
        'businessNumber': '791861073BC0001',
        'name': 'Foobar, Inc.'
    })

    assert entity is not None
    dictionary = entity.as_dict()
    assert dictionary['businessIdentifier'] == 'CP1234567'


def test_entity_find_by_business_id(session):  # pylint:disable=unused-argument
    """Assert that an Entity can be retrieved by business identifier."""
    factory_entity_model(business_identifier='CP1234567')
    entity = EntityService.find_by_business_identifier('CP1234567')

    assert entity is not None
    dictionary = entity.as_dict()
    assert dictionary['businessIdentifier'] == 'CP1234567'


def test_entity_find_by_business_id_no_model(session):  # pylint:disable=unused-argument
    """Assert that an Entity which does not exist cannot be retrieved."""
    entity = EntityService.find_by_business_identifier('CP1234567')

    assert entity is None


def test_add_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an Entity."""
    entity_model = factory_entity_model(business_identifier='CP1234567')
    entity = EntityService(entity_model)
    entity.add_contact(TEST_CONTACT_INFO)

    dictionary = entity.as_dict()
    assert dictionary['contacts']
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TEST_CONTACT_INFO['email']


def test_add_contact_duplicate(session):  # pylint:disable=unused-argument
    """Assert that a contact cannot be added to an Entity if that Entity already has a contact."""
    entity_model = factory_entity_model(business_identifier='CP1234567')
    entity = EntityService(entity_model)
    entity.add_contact(TEST_CONTACT_INFO)

    with pytest.raises(BusinessException) as exception:
        entity.add_contact(TEST_UPDATED_CONTACT_INFO)
    assert exception.value.code == Error.DATA_ALREADY_EXISTS.name


def test_update_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact for an existing Entity can be updated."""
    entity_model = factory_entity_model(business_identifier='CP1234567')
    entity = EntityService(entity_model)
    entity.add_contact(TEST_CONTACT_INFO)

    dictionary = entity.as_dict()
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == \
        TEST_CONTACT_INFO['email']

    entity.update_contact(TEST_UPDATED_CONTACT_INFO)

    dictionary = None
    dictionary = entity.as_dict()
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == \
        TEST_UPDATED_CONTACT_INFO['email']


def test_update_contact_no_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact for a non-existent contact cannot be updated."""
    entity_model = factory_entity_model(business_identifier='CP1234567')
    entity = EntityService(entity_model)

    with pytest.raises(BusinessException) as exception:
        entity.update_contact(TEST_UPDATED_CONTACT_INFO)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_get_contact_by_business_identifier(session):  # pylint:disable=unused-argument
    """Assert that a contact can be retrieved by the associated business id."""
    entity_model = factory_entity_model(business_identifier='CP1234567')
    entity = EntityService(entity_model)
    entity.add_contact(TEST_CONTACT_INFO)

    contact = entity.get_contact()
    assert contact is not None
    assert contact.email == TEST_CONTACT_INFO['email']


def test_get_contact_by_business_identifier_no_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact cannot be retrieved from an entity with no contact."""
    entity_model = factory_entity_model(business_identifier='CP1234567')
    entity = EntityService(entity_model)
    contact = entity.get_contact()
    assert contact is None


def test_validate_pass_code(app, session):  # pylint:disable=unused-argument
    """Assert that a valid passcode can be correctly validated."""
    entity_model = factory_entity_model(business_identifier='CP1234567', pass_code='12345678')
    entity = EntityService(entity_model)

    validated = entity.validate_pass_code(entity_model.pass_code)
    assert validated


def test_validate_invalid_pass_code(app, session):  # pylint:disable=unused-argument
    """Assert that an invalid passcode in not validated."""
    entity_model = factory_entity_model(business_identifier='CP1234567', pass_code='12345678')
    entity = EntityService(entity_model)

    validated = entity.validate_pass_code('1234')
    assert not validated

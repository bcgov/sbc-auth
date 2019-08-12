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
    'emailAddress': 'foo@bar.com'
}

TEST_UPDATED_CONTACT_INFO = {
    'emailAddress': 'bar@foo.com'
}


def factory_entity_model(business_identifier):
    """Return a valid entity object with the provided fields."""
    entity = EntityModel(business_identifier=business_identifier)
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
        'businessIdentifier': 'CP1234567'
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

    updated_entity = EntityService.add_contact(entity.as_dict()['businessIdentifier'], TEST_CONTACT_INFO)

    assert updated_entity is not None
    dictionary = updated_entity.as_dict()
    assert dictionary['contacts']
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['contact']['emailAddress'] == TEST_CONTACT_INFO['emailAddress']


def test_add_contact_no_entity(session):  # pylint:disable=unused-argument
    """Assert that a contact cannot be added to an Entity that does not exist."""
    with pytest.raises(BusinessException) as exception:
        EntityService.add_contact('non_existant_entity', TEST_CONTACT_INFO)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_add_contact_duplicate(session):  # pylint:disable=unused-argument
    """Assert that a contact cannot be added to an Entity if that Entity already has a contact."""
    entity_model = factory_entity_model(business_identifier='CP1234567')
    entity = EntityService(entity_model)
    EntityService.add_contact(entity.as_dict()['businessIdentifier'], TEST_CONTACT_INFO)

    with pytest.raises(BusinessException) as exception:
        EntityService.add_contact(entity.as_dict()['businessIdentifier'], TEST_UPDATED_CONTACT_INFO)
    assert exception.value.code == Error.DATA_CONFLICT.name


def test_update_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact for an existing Entity can be updated."""
    entity_model = factory_entity_model(business_identifier='CP1234567')
    entity = EntityService(entity_model)
    entity = EntityService.add_contact(entity.as_dict()['businessIdentifier'], TEST_CONTACT_INFO)

    assert entity is not None
    dictionary = entity.as_dict()
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['contact']['emailAddress'] == \
        TEST_CONTACT_INFO['emailAddress']

    updated_entity = EntityService.update_contact(entity.as_dict()['businessIdentifier'], TEST_UPDATED_CONTACT_INFO)

    dictionary = None
    dictionary = updated_entity.as_dict()
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['contact']['emailAddress'] == \
        TEST_UPDATED_CONTACT_INFO['emailAddress']


def test_update_contact_no_entity(session):  # pylint:disable=unused-argument
    """Assert that a contact for a non-existent Entity cannot be updated."""
    with pytest.raises(BusinessException) as exception:
        EntityService.update_contact('non_existant_entity', TEST_UPDATED_CONTACT_INFO)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_update_contact_no_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact for a non-existent contact cannot be updated."""
    factory_entity_model(business_identifier='CP1234567')

    with pytest.raises(BusinessException) as exception:
        EntityService.update_contact('CP1234567', TEST_UPDATED_CONTACT_INFO)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_get_contact_by_business_identifier(session):  # pylint:disable=unused-argument
    """Assert that a contact can be retrieved by the associated business id."""
    entity_model = factory_entity_model(business_identifier='CP1234567')
    entity = EntityService(entity_model)
    entity = EntityService.add_contact(entity.as_dict()['businessIdentifier'], TEST_CONTACT_INFO)

    contact = EntityService.get_contact_for_business('CP1234567')
    assert contact is not None
    assert contact.email == TEST_CONTACT_INFO['emailAddress']


def test_get_contact_by_business_identifier_no_entity(session):  # pylint:disable=unused-argument
    """Assert that a contact cannot be retrieved from a non-existent entity."""
    contact = EntityService.get_contact_for_business('CP1234567')
    assert contact is None


def test_get_contact_by_business_identifier_no_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact cannot be retrieved from an entity with no contact."""
    factory_entity_model(business_identifier='CP1234567')
    contact = EntityService.get_contact_for_business('CP1234567')
    assert contact is None

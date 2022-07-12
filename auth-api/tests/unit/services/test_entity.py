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
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.services.entity import Entity as EntityService
from tests.utilities.factory_scenarios import TestContactInfo, TestEntityInfo, TestJwtClaims, TestUserInfo
from tests.utilities.factory_utils import (
    factory_contact_model, factory_entity_model, factory_org_service, patch_token_info)


def test_as_dict(session):  # pylint:disable=unused-argument
    """Assert that the Entity is exported correctly as a dictionary."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)

    dictionary = entity.as_dict()
    assert dictionary['business_identifier'] == TestEntityInfo.entity1['businessIdentifier']


def test_save_entity_new(session):  # pylint:disable=unused-argument
    """Assert that an Entity can be created from a dictionary."""
    entity = EntityService.save_entity({
        'businessIdentifier': TestEntityInfo.entity_passcode['businessIdentifier'],
        'businessNumber': TestEntityInfo.entity_passcode['businessNumber'],
        'passCode': TestEntityInfo.entity_passcode['passCode'],
        'name': TestEntityInfo.entity_passcode['name'],
        'corpTypeCode': TestEntityInfo.entity_passcode['corpTypeCode']
    })

    assert entity is not None
    dictionary = entity.as_dict()
    assert dictionary['business_identifier'] == TestEntityInfo.entity_passcode['businessIdentifier']


def test_save_entity_existing(session):  # pylint:disable=unused-argument
    """Assert that an Entity can be updated from a dictionary."""
    entity = EntityService.save_entity({
        'businessIdentifier': TestEntityInfo.entity_passcode['businessIdentifier'],
        'businessNumber': TestEntityInfo.entity_passcode['businessNumber'],
        'passCode': TestEntityInfo.entity_passcode['passCode'],
        'name': TestEntityInfo.entity_passcode['name'],
        'corpTypeCode': TestEntityInfo.entity_passcode['corpTypeCode']
    })

    assert entity

    updated_entity_info = {
        'businessIdentifier': TestEntityInfo.entity_passcode2['businessIdentifier'],
        'businessNumber': TestEntityInfo.entity_passcode2['businessNumber'],
        'passCode': TestEntityInfo.entity_passcode['passCode'],
        'name': TestEntityInfo.entity_passcode['name'],
        'corpTypeCode': TestEntityInfo.entity_passcode['corpTypeCode']
    }

    updated_entity = EntityService.save_entity(updated_entity_info)

    assert updated_entity
    assert updated_entity.as_dict()['name'] == updated_entity_info['name']
    assert updated_entity.as_dict()['business_number'] == updated_entity_info['businessNumber']


def test_update_entity_existing_success(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Entity can be updated from a dictionary."""
    entity = EntityService.save_entity({
        'businessIdentifier': TestEntityInfo.bc_entity_passcode3['businessIdentifier'],
        'businessNumber': TestEntityInfo.bc_entity_passcode3['businessNumber'],
        'passCode': TestEntityInfo.bc_entity_passcode3['passCode'],
        'name': TestEntityInfo.bc_entity_passcode3['name'],
        'corpTypeCode': TestEntityInfo.bc_entity_passcode3['corpTypeCode']
    })

    assert entity
    assert entity.as_dict()['corp_type']['code'] == 'BC'

    updated_entity_info = {
        'businessIdentifier': TestEntityInfo.bc_entity_passcode4['businessIdentifier'],
        'businessNumber': TestEntityInfo.bc_entity_passcode4['businessNumber'],
        'name': TestEntityInfo.bc_entity_passcode4['name'],
        'corpTypeCode': TestEntityInfo.bc_entity_passcode4['corpTypeCode']
    }
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']

    patch_token_info({'loginSource': '', 'realm_access': {'roles': ['system']}, 'corp_type': 'BC'}, monkeypatch)
    updated_entity = EntityService.update_entity(entity.as_dict().get('business_identifier'), updated_entity_info)

    assert updated_entity
    assert updated_entity.as_dict()['name'] == updated_entity_info['name']
    assert updated_entity.as_dict()['business_number'] == updated_entity_info['businessNumber']


def test_update_entity_existing_failures(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Entity can be updated from a dictionary."""
    entity = EntityService.save_entity({
        'businessIdentifier': TestEntityInfo.bc_entity_passcode3['businessIdentifier'],
        'businessNumber': TestEntityInfo.bc_entity_passcode3['businessNumber'],
        'passCode': TestEntityInfo.bc_entity_passcode3['passCode'],
        'name': TestEntityInfo.bc_entity_passcode3['name'],
        'corpTypeCode': TestEntityInfo.bc_entity_passcode3['corpTypeCode']
    })

    assert entity
    assert entity.as_dict()['corp_type']['code'] == 'BC'

    updated_entity_info = {
        'businessIdentifier': TestEntityInfo.bc_entity_passcode4['businessIdentifier'],
        'businessNumber': TestEntityInfo.bc_entity_passcode4['businessNumber'],
        'name': TestEntityInfo.bc_entity_passcode4['name'],
        'corpTypeCode': TestEntityInfo.bc_entity_passcode4['corpTypeCode']
    }
    user_with_token = TestUserInfo.user_test
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']

    with pytest.raises(BusinessException) as exception:
        patch_token_info({'loginSource': '', 'realm_access': {'roles': ['system']},
                          'corp_type': 'INVALID_CP'}, monkeypatch)
        EntityService.update_entity('invalidbusinessnumber', updated_entity_info)

    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_save_entity_no_input(session):  # pylint:disable=unused-argument
    """Assert that an Entity can not be updated with no input."""
    updated_entity = EntityService.save_entity(None)

    assert updated_entity is None


def test_entity_find_by_business_id(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Entity can be retrieved by business identifier."""
    factory_entity_model()
    entity = EntityService.find_by_business_identifier(TestEntityInfo.entity1['businessIdentifier'])

    assert entity is not None
    dictionary = entity.as_dict()
    assert dictionary['business_identifier'] == TestEntityInfo.entity1['businessIdentifier']


def test_entity_find_by_business_id_no_model(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Entity which does not exist cannot be retrieved."""
    entity = EntityService.find_by_business_identifier(TestEntityInfo.entity1['businessIdentifier'])

    assert entity is None


def test_entity_find_by_entity_id(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Entity can be retrieved by entity identifier."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)

    entity = EntityService.find_by_entity_id(entity.identifier)

    assert entity is not None
    dictionary = entity.as_dict()
    assert dictionary['business_identifier'] == TestEntityInfo.entity1['businessIdentifier']


def test_entity_find_by_entity_id_no_id(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Entity can not be retrieved when no id input or entity not exists."""
    entity = EntityService.find_by_entity_id(None)

    assert entity is None

    entity = EntityService.find_by_entity_id(9999)

    assert entity is None


def test_add_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an Entity."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)
    entity.add_contact(TestContactInfo.contact1)

    dictionary = entity.as_dict()
    assert dictionary['contacts']
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TestContactInfo.contact1['email']


def test_add_contact_duplicate(session):  # pylint:disable=unused-argument
    """Assert that a contact cannot be added to an Entity if that Entity already has a contact."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)
    entity.add_contact(TestContactInfo.contact1)

    with pytest.raises(BusinessException) as exception:
        entity.add_contact(TestContactInfo.contact2)
    assert exception.value.code == Error.DATA_ALREADY_EXISTS.name


def test_update_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact for an existing Entity can be updated."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)
    entity.add_contact(TestContactInfo.contact1)

    dictionary = entity.as_dict()
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TestContactInfo.contact1['email']

    entity.update_contact(TestContactInfo.contact2)

    dictionary = None
    dictionary = entity.as_dict()
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TestContactInfo.contact2['email']


def test_update_contact_no_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact for a non-existent contact cannot be updated."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)

    with pytest.raises(BusinessException) as exception:
        entity.update_contact(TestContactInfo.contact2)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_get_contact_by_business_identifier(session):  # pylint:disable=unused-argument
    """Assert that a contact can be retrieved by the associated business id."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)
    entity.add_contact(TestContactInfo.contact1)

    contact = entity.get_contact()
    assert contact is not None
    assert contact.email == TestContactInfo.contact1['email']


def test_get_contact_by_business_identifier_no_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact cannot be retrieved from an entity with no contact."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)
    contact = entity.get_contact()
    assert contact is None


def test_delete_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact can be deleted to an Entity."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)
    entity.add_contact(TestContactInfo.contact1)

    updated_entity = entity.delete_contact()
    dictionary = updated_entity.as_dict()
    assert not dictionary['contacts']


def test_delete_contact_no_entity(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that a contact can not be deleted without entity."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)
    entity.add_contact(TestContactInfo.contact1)

    updated_entity = entity.delete_contact()

    with pytest.raises(BusinessException) as exception:
        updated_entity.delete_contact()

    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_delete_contact_entity_link(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that a contact can not be deleted without entity."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)

    org = factory_org_service()
    org_dictionary = org.as_dict()
    org_id = org_dictionary['id']

    contact = factory_contact_model()

    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.entity = entity._model  # pylint:disable=protected-access
    contact_link.org = org._model  # pylint:disable=protected-access
    contact_link.commit()

    updated_entity = entity.delete_contact()

    dictionary = None
    dictionary = updated_entity.as_dict()
    assert len(dictionary['contacts']) == 0

    delete_contact_link = ContactLinkModel.find_by_entity_id(entity.identifier)
    assert not delete_contact_link

    exist_contact_link = ContactLinkModel.find_by_org_id(org_id)
    assert exist_contact_link


def test_validate_pass_code(app, session):  # pylint:disable=unused-argument
    """Assert that a valid passcode can be correctly validated."""
    entity_model = factory_entity_model(entity_info=TestEntityInfo.entity_passcode)
    entity = EntityService(entity_model)

    validated = entity.validate_pass_code(entity_model.pass_code)
    assert validated


def test_validate_invalid_pass_code(app, session):  # pylint:disable=unused-argument
    """Assert that an invalid passcode in not validated."""
    entity_model = factory_entity_model(entity_info=TestEntityInfo.entity_passcode)
    entity = EntityService(entity_model)

    validated = entity.validate_pass_code('222222222')
    assert not validated


def test_delete_entity(app, session):  # pylint:disable=unused-argument
    """Assert that an entity can be deleted."""
    entity_model = factory_entity_model()
    entity = EntityService(entity_model)

    org = factory_org_service()

    contact = factory_contact_model()

    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.entity = entity._model  # pylint:disable=protected-access
    contact_link.org = org._model  # pylint:disable=protected-access
    contact_link.commit()

    entity.delete()

    entity = EntityService.find_by_entity_id(entity.identifier)

    assert entity is None


def test_reset_pass_code(app, session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that the new passcode in not the same as old passcode."""
    entity_model = factory_entity_model(entity_info=TestEntityInfo.entity_passcode)

    entity = EntityService(entity_model)
    old_passcode = entity.pass_code
    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    entity.reset_passcode(entity.business_identifier, '')
    new_passcode = entity.pass_code

    assert old_passcode != new_passcode

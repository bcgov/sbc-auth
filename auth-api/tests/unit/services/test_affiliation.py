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
"""Tests for the Affiliation service.

Test suite to ensure that the Affiliation service routines are working as expected.
"""
from unittest.mock import patch

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.org import Org as OrgModel
from auth_api.services import Affiliation as AffiliationService
from tests.utilities.factory_scenarios import TestEntityInfo, TestOrgTypeInfo
from tests.utilities.factory_utils import factory_entity_service, factory_org_service


def test_create_affiliation(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['businessIdentifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation = AffiliationService.create_affiliation(org_id, business_identifier, {})
    assert affiliation
    assert affiliation.entity.identifier == entity_service.identifier
    assert affiliation.as_dict()['org']['id'] == org_dictionary['id']


def test_create_affiliation_no_org(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be created without org."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['businessIdentifier']

    with pytest.raises(BusinessException) as exception:
        AffiliationService.create_affiliation(None, business_identifier, {})
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_create_affiliation_no_entity(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be created without entity."""
    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    with pytest.raises(BusinessException) as exception:
        AffiliationService.create_affiliation(org_id, None, {})
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_create_affiliation_implicit(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be created when org is IMPLICIT."""
    entity_service1 = factory_entity_service()
    entity_dictionary1 = entity_service1.as_dict()
    business_identifier1 = entity_dictionary1['businessIdentifier']

    org_service = factory_org_service(org_type_info=TestOrgTypeInfo.implicit)
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    pass_code = '111111111'

    with pytest.raises(BusinessException) as exception:
        AffiliationService.create_affiliation(org_id, business_identifier1, pass_code, {})

        found_org = OrgModel.query.filter_by(id=org_id).first()
        assert found_org is None

    assert exception.value.code == Error.INVALID_USER_CREDENTIALS.name


def test_create_affiliation_with_passcode(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_passcode)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['businessIdentifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation = AffiliationService.create_affiliation(org_id,
                                                        business_identifier,
                                                        TestEntityInfo.entity_passcode['passCode'],
                                                        {})
    assert affiliation
    assert affiliation.entity.identifier == entity_service.identifier
    assert affiliation.as_dict()['org']['id'] == org_dictionary['id']


def test_create_affiliation_with_passcode_no_passcode_input(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be created with a passcode entity and no passcode input parameter."""
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_passcode)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['businessIdentifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    with pytest.raises(BusinessException) as exception:
        AffiliationService.create_affiliation(org_id, business_identifier)

    assert exception.value.code == Error.INVALID_USER_CREDENTIALS.name


def test_create_affiliation_exists(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be created affiliation exists."""
    entity_service1 = factory_entity_service(entity_info=TestEntityInfo.entity_passcode)
    entity_dictionary1 = entity_service1.as_dict()
    business_identifier1 = entity_dictionary1['businessIdentifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    pass_code = '111111111'

    # create first row in affiliation table
    AffiliationService.create_affiliation(org_id, business_identifier1, pass_code, {})

    with pytest.raises(BusinessException) as exception:
        AffiliationService.create_affiliation(org_id, business_identifier1, pass_code, {})
    assert exception.value.code == Error.DATA_ALREADY_EXISTS.name


def test_find_affiliated_entities_by_org_id(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service1 = factory_entity_service()
    entity_dictionary1 = entity_service1.as_dict()
    business_identifier1 = entity_dictionary1['businessIdentifier']

    entity_service2 = factory_entity_service(entity_info=TestEntityInfo.entity2)
    entity_dictionary2 = entity_service2.as_dict()
    business_identifier2 = entity_dictionary2['businessIdentifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    # create first row in affiliation table
    AffiliationService.create_affiliation(org_id, business_identifier1)
    # create second row in affiliation table
    AffiliationService.create_affiliation(org_id, business_identifier2)

    affiliated_entities = AffiliationService.find_affiliated_entities_by_org_id(org_id)

    assert affiliated_entities
    assert len(affiliated_entities) == 2
    assert affiliated_entities[0]['businessIdentifier'] == entity_dictionary1['businessIdentifier']


def test_find_affiliated_entities_by_org_id_no_org(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be find without org id or org id not exists."""
    with pytest.raises(BusinessException) as exception:
        AffiliationService.find_affiliated_entities_by_org_id(None)
    assert exception.value.code == Error.DATA_NOT_FOUND.name

    with pytest.raises(BusinessException) as exception:
        AffiliationService.find_affiliated_entities_by_org_id(999999)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_find_affiliated_entities_by_org_id_no_affiliation(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be find without affiliation."""
    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    with patch.object(AffiliationModel, 'find_affiliations_by_org_id', return_value=None):
        with pytest.raises(BusinessException) as exception:
            AffiliationService.find_affiliated_entities_by_org_id(org_id)

    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_delete_affiliation(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an affiliation can be deleted."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['businessIdentifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation = AffiliationService.create_affiliation(org_id, business_identifier)

    AffiliationService.delete_affiliation(org_id=org_id, business_identifier=business_identifier)

    found_affiliation = AffiliationModel.query.filter_by(id=affiliation.identifier).first()
    assert found_affiliation is None


def test_delete_affiliation_no_org(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an affiliation can not be deleted without org."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['businessIdentifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    AffiliationService.create_affiliation(org_id, business_identifier)

    with pytest.raises(BusinessException) as exception:
        AffiliationService.delete_affiliation(org_id=None, business_identifier=business_identifier)

    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_delete_affiliation_no_entity(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an affiliation can not be deleted without entity."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['businessIdentifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    AffiliationService.create_affiliation(org_id, business_identifier)

    with pytest.raises(BusinessException) as exception:
        AffiliationService.delete_affiliation(org_id=org_id, business_identifier=None)

    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_delete_affiliation_no_affiliation(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an affiliation can not be deleted without affiliation."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['businessIdentifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    AffiliationService.create_affiliation(org_id, business_identifier)
    AffiliationService.delete_affiliation(org_id=org_id, business_identifier=business_identifier)

    with pytest.raises(BusinessException) as exception:
        AffiliationService.delete_affiliation(org_id=org_id, business_identifier=business_identifier)

    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_delete_affiliation_implicit(session, auth_mock):  # pylint:disable=unused-argument
    """Assert that an affiliation can be deleted."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['businessIdentifier']

    org_service = factory_org_service(org_type_info=TestOrgTypeInfo.implicit)
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation = AffiliationService.create_affiliation(org_id, business_identifier)

    AffiliationService.delete_affiliation(org_id=org_id, business_identifier=business_identifier)

    found_affiliation = AffiliationModel.query.filter_by(id=affiliation.identifier).first()
    assert found_affiliation is None

    found_org = OrgModel.query.filter_by(id=org_id).first()
    assert found_org is None

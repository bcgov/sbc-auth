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
from auth_api.models.org_type import OrgType as OrgTypeModel
from auth_api.models.org_status import OrgStatus as OrgStatusModel
from auth_api.models.payment_type import PaymentType as PaymentTypeModel
from auth_api.models.org import Org as OrgModel
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.exceptions import BusinessException
import pytest
from auth_api.services import Org as OrgService
from auth_api.services import Entity as EntityService
from auth_api.services import Affiliation as AffiliationService


def factory_entity_service():
    entity = EntityModel(business_identifier='CP1234567')
    entity.save()
    entity_service = EntityService(entity)
    return entity_service


def factory_org_service(name):
    """Produce a templated org model."""
    org_type = OrgTypeModel(code='TEST', desc='Test')
    org_type.save()

    org_status = OrgStatusModel(code='TEST', desc='Test')
    org_status.save()

    preferred_payment = PaymentTypeModel(code='TEST', desc='Test')
    preferred_payment.save()

    org = OrgModel(name=name)
    org.org_type = org_type
    org.org_status = org_status
    org.preferred_payment = preferred_payment
    org.save()

    org_service = OrgService(org)

    return org_service


def factory_affiliation_service(entity_id, org_id):
    affiliation = AffiliationModel(entity=entity_id, org=org_id)
    affiliation.save()
    affiliation_service = AffiliationService(affiliation)
    return affiliation_service


def test_create_affiliation(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    entity_id = entity_dictionary['id']

    org_service = factory_org_service(name='My Test Org')
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation_info = {
        'entity': entity_id
    }

    affiliation_dictionary = AffiliationService.create_affiliation(org_id, affiliation_info)
    assert affiliation_dictionary
    assert affiliation_dictionary['entityInfo']['businessIdentifier'] == 'CP1234567'


def test_update_affiliation(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    entity_id = entity_dictionary['id']

    org_service = factory_org_service(name='My Test Org')
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation_info = {
        'entity': entity_id
    }

    affiliation_dictionary = AffiliationService.create_affiliation(org_id, affiliation_info)
    assert affiliation_dictionary
    assert affiliation_dictionary['entityInfo']['businessIdentifier'] == 'CP1234567'

    entity2 = EntityModel(business_identifier='CP7654321')
    entity2.save()
    entity2_service = EntityService(entity2)
    entity2_dictionary = entity2_service.as_dict()
    entity2_id = entity2_dictionary['id']

    affiliation_info2 = {
        'entity': entity2_id
    }

    affiliation_service2 = AffiliationService.update_affiliation(org_id, affiliation_dictionary['id'], affiliation_info2)
    assert affiliation_service2
    affiliation_dictionary2 = affiliation_service2.as_dict()
    assert affiliation_dictionary2['entityInfo']['businessIdentifier'] == 'CP7654321'


def test_find_affiliation_by_ids(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    entity_id = entity_dictionary['id']

    org_service = factory_org_service(name='My Test Org')
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation_service = factory_affiliation_service(entity_id, org_id)
    assert affiliation_service
    affiliation_dictionary = affiliation_service.as_dict()
    assert affiliation_dictionary['entityInfo']['businessIdentifier'] == 'CP1234567'
    affiliation_id = affiliation_dictionary['id']

    affiliation_dictionary2 = AffiliationService.find_affiliation_by_ids(org_id, affiliation_id)
    assert affiliation_dictionary2
    assert affiliation_dictionary2['entityInfo']['businessIdentifier'] == 'CP1234567'


def test_find_affiliation_by_invalid_ids(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    with pytest.raises(BusinessException) as excinfo:
        AffiliationService.find_affiliation_by_ids(123, 456)
    assert excinfo.type == BusinessException


def test_find_affiliations_by_org_id(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    entity_id = entity_dictionary['id']

    org_service = factory_org_service(name='My Test Org')
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation_info = {
        'entity': entity_id
    }

    #create first row in affiliation table
    affiliation_service = AffiliationService.create_affiliation(org_id, affiliation_info)
    #create second row in affiliation table
    affiliation_service = AffiliationService.create_affiliation(org_id, affiliation_info)

    affiliation_dictionary = AffiliationService.find_affiliations_by_org_id(org_id)

    assert affiliation_dictionary
    assert len(affiliation_dictionary['items']) == 2
    assert affiliation_dictionary['items'][1]['entityInfo']['businessIdentifier'] == 'CP1234567'


def test_find_affiliations_by_invalid_org_id_in_org(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    with pytest.raises(BusinessException) as excinfo:
        AffiliationService.find_affiliations_by_org_id(123456)
    assert excinfo.type == BusinessException

def test_find_affiliations_by_invalid_org_id_in_affiliation(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    org_service = factory_org_service(name='My Test Org')
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    # no org_id in affiliation table.
    affiliation_dictionary = AffiliationService.find_affiliations_by_org_id(org_id)
    assert len(affiliation_dictionary['items']) == 0

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
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.entity import Entity as EntityModel
from auth_api.models.org import Org as OrgModel
from auth_api.models.org_status import OrgStatus as OrgStatusModel
from auth_api.models.org_type import OrgType as OrgTypeModel
from auth_api.models.payment_type import PaymentType as PaymentTypeModel
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import Entity as EntityService
from auth_api.services import Org as OrgService


def factory_entity_service(business_identifier='CP1234567', business_number='791861073BC0001', name='Foobar, Inc.'):
    """Produce a templated entity model."""
    entity = EntityModel.create_from_dict({
        'business_identifier': business_identifier,
        'business_number': business_number,
        'name': name
    })
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
    """Produce a templated affiliation service."""
    affiliation = AffiliationModel(entity=entity_id, org=org_id)
    affiliation.save()
    affiliation_service = AffiliationService(affiliation)
    return affiliation_service


def test_create_affiliation(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['businessIdentifier']

    org_service = factory_org_service(name='My Test Org')
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation = AffiliationService.create_affiliation(org_id, business_identifier)
    assert affiliation
    assert affiliation.entity.identifier == entity_service.identifier
    assert affiliation.as_dict()['org']['id'] == org_dictionary['id']


def test_find_affiliated_entities_by_org_id(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service1 = factory_entity_service(business_identifier='CP555')
    entity_dictionary1 = entity_service1.as_dict()
    business_identifier1 = entity_dictionary1['businessIdentifier']

    entity_service2 = factory_entity_service(business_identifier='CP556')
    entity_dictionary2 = entity_service2.as_dict()
    business_identifier2 = entity_dictionary2['businessIdentifier']

    org_service = factory_org_service(name='My Test Org')
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


def test_delete_affiliation(session):  # pylint:disable=unused-argument
    """Assert that an affiliation can be deleted."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['businessIdentifier']

    org_service = factory_org_service(name='My Test Org')
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation = AffiliationService.create_affiliation(org_id, business_identifier)

    AffiliationService.delete_affiliation(org_id=org_id, business_identifier=business_identifier)

    found_affiliation = AffiliationModel.query.filter_by(id=affiliation.identifier).first()
    assert found_affiliation is None

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
"""Tests for the Affiliation model.

Test suite to ensure that the Affiliation model routines are working as expected.
"""
import pytest

from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Entity as EntityModel
from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.models import PaymentType as PaymentTypeModel


def factory_entity_model():
    """Produce a templated entity model."""
    entity = EntityModel(business_identifier='CP1234567', business_number='791861073BC0001', name='Foobar, Inc.',
                         corp_type_code='CP')
    entity.save()
    return entity


def factory_org_model(name):
    """Produce a templated org model."""
    org_type = OrgTypeModel(code='TEST', description='Test')
    org_type.save()

    org_status = OrgStatusModel(code='TEST', description='Test')
    org_status.save()

    preferred_payment = PaymentTypeModel(code='TEST', description='Test')
    preferred_payment.save()

    org = OrgModel(name=name)
    org.org_type = org_type
    org.org_status = org_status
    org.preferred_payment = preferred_payment
    org.save()

    return org


def factory_affiliation_model(entity_id, org_id, environment=None):
    """Produce a templated affiliation model."""
    affiliation = AffiliationModel(entity_id=entity_id, org_id=org_id, environment=environment)
    affiliation.save()
    return affiliation


def test_affiliation(session):  # pylint:disable=unused-argument
    """Assert that a Affiliation can be stored in the service."""
    entity = factory_entity_model()
    org = factory_org_model(name='My Test Org')
    affiliation = factory_affiliation_model(entity.id, org.id)

    assert entity.id is not None
    assert org.id is not None
    assert affiliation.id is not None
    assert affiliation.environment is None


def test_find_affiliation_by_ids(session):  # pylint:disable=unused-argument
    """Assert that a affiliation can be retrieved via the org id and affiliation id."""
    entity = factory_entity_model()
    org = factory_org_model(name='My Test Org')
    affiliation = factory_affiliation_model(entity.id, org.id)

    result_affiliation = affiliation.find_affiliation_by_ids(org_id=org.id, affiliation_id=affiliation.id)
    assert result_affiliation is not None


@pytest.mark.parametrize('environment', ['test', None])
def test_find_affiliations_by_org_id(session, environment):  # pylint:disable=unused-argument
    """Assert that a affiliation can be retrieved via affiliation id."""
    entity = factory_entity_model()
    org = factory_org_model(name='My Test Org')
    affiliation = factory_affiliation_model(entity.id, org.id, environment)

    result_affiliation = affiliation.find_affiliations_by_org_id(org_id=org.id, environment=environment)
    assert result_affiliation is not None


@pytest.mark.parametrize('environment', ['test', None])
def test_find_affiliation_by_org_and_entity_ids(session, environment):  # pylint:disable=unused-argument
    """Assert that affiliations can be retrieved via the org id."""
    entity = factory_entity_model()
    org = factory_org_model(name='My Test Org')
    affiliation = factory_affiliation_model(entity.id, org.id, environment)

    result_affiliations = affiliation.find_affiliation_by_org_and_entity_ids(org_id=org.id, entity_id=entity.id,
                                                                             environment=environment)
    assert result_affiliations is not None


@pytest.mark.parametrize('environment', ['test', None])
def test_find_affiliation_by_org_id_and_business_identifier(session, environment):  # pylint:disable=unused-argument
    """Assert that affiliations can be retrieved via the org id and business identifier."""
    entity = factory_entity_model()
    org = factory_org_model(name='My Test Org')
    affiliation = factory_affiliation_model(entity.id, org.id, environment)

    result_affiliations = affiliation.find_affiliation_by_org_id_and_business_identifier(org.id,
                                                                                         entity.business_identifier,
                                                                                         environment)
    assert result_affiliations is not None

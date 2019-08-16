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
"""Tests for the Org model.

Test suite to ensure that the Org model routines are working as expected.
"""

from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.models import PaymentType as PaymentTypeModel


def factory_org_model(name, session):
    """Produce a templated org model."""
    org_type = OrgTypeModel(code='TEST', desc='Test')
    session.add(org_type)
    session.commit()

    org_status = OrgStatusModel(code='TEST', desc='Test')
    session.add(org_status)
    session.commit()

    preferred_payment = PaymentTypeModel(code='TEST', desc='Test')
    session.add(preferred_payment)
    session.commit()

    org = OrgModel(name=name)
    org.org_type = org_type
    org.org_status = org_status
    org.preferred_payment = preferred_payment
    org.save()

    return org


def test_org(session):
    """Assert that an Org can be stored in the service."""
    org = factory_org_model(name='My Test Org', session=session)
    session.add(org)
    session.commit()
    assert org.id is not None


def test_org_create_from_dictionary(session):  # pylint:disable=unused-argument
    """Assert that an Org can be created from a dictionary."""
    org_info = {
        'name': 'My Test Org'
    }

    org_model = OrgModel.create_from_dict(org_info)
    assert org_model
    assert org_model.id
    assert org_model.name == org_info['name']


def test_org_find_by_id(session):  # pylint:disable=unused-argument
    """Assert that an Org can retrieved by its id."""
    org = factory_org_model(name='My Test Org', session=session)
    session.add(org)
    session.commit()

    found_org = OrgModel.find_by_org_id(org.id)
    assert found_org
    assert found_org.name == org.name


def test_update_org_from_dict(session):  # pylint:disable=unused-argument
    """Assert that an Org can be updated from a dictionary."""
    org = factory_org_model(name='My Test Org', session=session)
    session.add(org)
    session.commit()

    update_dictionary = {
        'name': 'My Updated Test Org'
    }
    org.update_org_from_dict(update_dictionary)
    assert org
    assert org.name == update_dictionary['name']

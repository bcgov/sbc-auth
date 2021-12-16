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
from auth_api.utils.enums import OrgStatus as OrgStatusEnum
from tests.utilities.factory_utils import factory_user_model


def factory_org_model(name, session):
    """Produce a templated org model."""
    org_type = OrgTypeModel(code='TEST', description='Test')
    session.add(org_type)
    session.commit()

    org_status = OrgStatusModel(code='TEST', description='Test')
    session.add(org_status)
    session.commit()

    preferred_payment = PaymentTypeModel(code='TEST', description='Test')
    session.add(preferred_payment)
    session.commit()
    org = OrgModel(name=name)
    org.org_type = org_type
    org.org_status = OrgStatusModel.get_default_status()
    org.preferred_payment = preferred_payment
    org.branch_name = ''
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

    org_model = OrgModel.create_from_dict(org_info).save()
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


def test_org_find_by_name(session):  # pylint:disable=unused-argument
    """Assert that an Org can retrieved by its name."""
    org = factory_org_model(name='My Test Org', session=session)
    session.add(org)
    session.commit()

    found_org = OrgModel.find_by_org_name(org.name)
    assert found_org

    for org1 in found_org:
        assert org1.name == org.name


def test_org_find_by_name_inactive(session):  # pylint:disable=unused-argument
    """Assert that an inactive Org can not be retrieved by its name."""
    org = factory_org_model(name='My Test Org', session=session)
    session.add(org)
    session.commit()

    org.delete()

    found_org = OrgModel.find_by_org_name(org.name)
    assert len(found_org) == 0


def test_find_similar_org_by_name(session):  # pylint:disable=unused-argument
    """Assert that an Org can retrieved by its name."""
    org = factory_org_model(name='My Test Org', session=session)
    session.add(org)
    session.commit()

    found_org = OrgModel.find_similar_org_by_name(org.name)[0]
    assert found_org
    assert found_org.name == org.name

    found_org = OrgModel.find_similar_org_by_name('Test Or')
    assert not found_org


def test_find_similar_org_by_name_inactive(session):  # pylint:disable=unused-argument
    """Assert that an inactive Org can not be retrieved by its name."""
    org = factory_org_model(name='My Test Org', session=session)
    session.add(org)
    session.commit()

    org.delete()

    found_org = OrgModel.find_similar_org_by_name(org.name)
    assert not found_org


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


def test_count_org_from_dict(session):  # pylint:disable=unused-argument
    """Assert that an Org can be updated from a dictionary."""
    user = factory_user_model()
    org = factory_org_model(name='My Test Org', session=session)
    org.created_by_id = user.id
    session.add(org)
    session.commit()
    assert OrgModel.get_count_of_org_created_by_user_id(user.id) == 1


def test_create_from_dict(session):  # pylint:disable=unused-argument
    """Assert that an Org can be created from schema."""
    org_info = {
        'name': 'My Test Org'
    }

    result_org = OrgModel.create_from_dict(org_info).save()

    assert result_org.id is not None


def test_create_from_dict_no_schema(session):  # pylint:disable=unused-argument
    """Assert that an Org can not be created without schema."""
    result_org = OrgModel.create_from_dict(None)

    assert result_org is None


def test_delete(session):  # pylint:disable=unused-argument
    """Assert that an Org can be updated from a dictionary."""
    org = factory_org_model(name='My Test Org', session=session)
    session.add(org)
    session.commit()
    assert org.status_code == OrgStatusEnum.ACTIVE.value

    org.delete()
    assert org
    assert org.status_code == OrgStatusEnum.INACTIVE.value

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
"""Tests for the Org service.

Test suite to ensure that the Org service routines are working as expected.
"""

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.models import PaymentType as PaymentTypeModel
from auth_api.models import User as UserModel
from auth_api.services import Org as OrgService


TEST_ORG_INFO = {
    'name': 'My Test Org'
}

TEST_UPDATED_ORG_INFO = {
    'name': 'My Updated Test Org'
}

TEST_CONTACT_INFO = {
    'email': 'foo@bar.com'
}

TEST_UPDATED_CONTACT_INFO = {
    'email': 'bar@foo.com'
}


def factory_user_model(username,
                       firstname=None,
                       lastname=None,
                       roles=None,
                       keycloak_guid=None):
    """Return a valid user object stamped with the supplied designation."""
    user = UserModel(username=username,
                     firstname=firstname,
                     lastname=lastname,
                     roles=roles,
                     keycloak_guid=keycloak_guid)
    user.save()
    return user


def factory_org_service(session, name):
    """Produce a templated org service."""
    org_type = OrgTypeModel(code='TEST', desc='Test')
    session.add(org_type)
    session.commit()

    org_status = OrgStatusModel(code='TEST', desc='Test')
    session.add(org_status)
    session.commit()

    preferred_payment = PaymentTypeModel(code='TEST', desc='Test')
    session.add(preferred_payment)
    session.commit()

    org_model = OrgModel(name=name)
    org_model.org_type = org_type
    org_model.org_status = org_status
    org_model.preferred_payment = preferred_payment
    org_model.save()

    org = OrgService(org_model)

    return org


def test_as_dict(session):  # pylint:disable=unused-argument
    """Assert that the Org is exported correctly as a dictinoary."""
    org = factory_org_service(session, **TEST_ORG_INFO)

    dictionary = org.as_dict()
    assert dictionary
    assert dictionary['name'] == TEST_ORG_INFO['name']


def test_create_org(session):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    user = factory_user_model(username='testuser',
                              roles='{edit,uma_authorization,basic}',
                              keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    org = OrgService.create_org(TEST_ORG_INFO, user_id=user.id)
    assert org
    dictionary = org.as_dict()
    assert dictionary['name'] == TEST_ORG_INFO['name']


def test_update_org(session):  # pylint:disable=unused-argument
    """Assert that an Org can be updated."""
    org = factory_org_service(session, **TEST_ORG_INFO)

    org.update_org(TEST_UPDATED_ORG_INFO)

    dictionary = org.as_dict()
    assert dictionary['name'] == TEST_UPDATED_ORG_INFO['name']


def test_find_org_by_id(session):  # pylint:disable=unused-argument
    """Assert that an org can be retrieved by its id."""
    org = factory_org_service(session, **TEST_ORG_INFO)
    dictionary = org.as_dict()
    org_id = dictionary['id']

    found_org = OrgService.find_by_org_id(org_id)
    assert found_org
    dictionary = found_org.as_dict()
    assert dictionary['name'] == TEST_ORG_INFO['name']


def test_find_org_by_id_no_org(session):  # pylint:disable=unused-argument
    """Assert that an org which does not exist cannot be retrieved."""
    org = OrgService.find_by_org_id(99)
    assert org is None


def test_add_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an org."""
    org = factory_org_service(session, **TEST_ORG_INFO)
    org.add_contact(TEST_CONTACT_INFO)
    dictionary = org.as_dict()
    assert dictionary['contacts']
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TEST_CONTACT_INFO['email']


def test_add_contact_duplicate(session):  # pylint:disable=unused-argument
    """Assert that a contact cannot be added to an Org if that Org already has a contact."""
    org = factory_org_service(session, **TEST_ORG_INFO)
    org.add_contact(TEST_CONTACT_INFO)

    with pytest.raises(BusinessException) as exception:
        org.add_contact(TEST_UPDATED_CONTACT_INFO)
    assert exception.value.code == Error.DATA_ALREADY_EXISTS.name


def test_update_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact for an existing Org can be updated."""
    org = factory_org_service(session, **TEST_ORG_INFO)
    org.add_contact(TEST_CONTACT_INFO)

    dictionary = org.as_dict()
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == \
        TEST_CONTACT_INFO['email']

    org.update_contact(TEST_UPDATED_CONTACT_INFO)

    dictionary = org.as_dict()
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == \
        TEST_UPDATED_CONTACT_INFO['email']


def test_update_contact_no_contact(session):  # pylint:disable=unused-argument
    """Assert that a contact for a non-existent contact cannot be updated."""
    org = factory_org_service(session, **TEST_ORG_INFO)

    with pytest.raises(BusinessException) as exception:
        org.update_contact(TEST_UPDATED_CONTACT_INFO)
    assert exception.value.code == Error.DATA_NOT_FOUND.name

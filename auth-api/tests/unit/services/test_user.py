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

"""Tests to verify the User Service.

Test-Suite to ensure that the User Service is working as expected.
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
from auth_api.services import User as UserService


TEST_TOKEN = {
        'preferred_username': 'testuser',
        'sub': '1b20db59-19a0-4727-affe-c6f64309fd04',
        'realm_access': {
            'roles': [
                'edit',
                'uma_authorization',
                'basic'
            ]
        }
    }

TEST_CONTACT_INFO = {
    'email': 'foo@bar.com',
    'phone': '(555) 555-5555',
    'phoneExtension': '123'
}

TEST_UPDATED_CONTACT_INFO = {
    'email': 'bar@foo.com',
    'phone': '(555) 555-5555',
    'phoneExtension': '123'
}

TEST_ORG_INFO = {
    'name': 'My Test Org'
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


def test_as_dict(session):  # pylint: disable=unused-argument
    """Assert that a user is rendered correctly as a dictionary."""
    user_model = factory_user_model(username='testuser',
                                    roles='{edit,uma_authorization,basic}',
                                    keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    user = UserService(user_model)

    dictionary = user.as_dict()
    assert dictionary['username'] == 'testuser'
    assert dictionary['roles'] == '{edit,uma_authorization,basic}'
    assert dictionary['keycloak_guid'] == '1b20db59-19a0-4727-affe-c6f64309fd04'


def test_user_save_by_token(session):  # pylint: disable=unused-argument
    """Assert that a user can be created by token."""
    user = UserService.save_from_jwt_token(TEST_TOKEN)
    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['username'] == TEST_TOKEN['preferred_username']
    assert dictionary['keycloak_guid'] == TEST_TOKEN['sub']


def test_user_save_by_token_no_token(session):  # pylint: disable=unused-argument
    """Assert that a user cannot be created from an empty token."""
    user = UserService.save_from_jwt_token(None)
    assert user is None


def test_add_contact_to_user(session):  # pylint: disable=unused-argument
    """Assert that a contact can be added to a user."""
    factory_user_model(username='testuser',
                       roles='{edit,uma_authorization,basic}',
                       keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    user = UserService.add_contact(TEST_TOKEN, TEST_CONTACT_INFO)

    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['contacts']
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TEST_CONTACT_INFO['email']
    assert dictionary['contacts'][0]['phone'] == TEST_CONTACT_INFO['phone']
    assert dictionary['contacts'][0]['phoneExtension'] == TEST_CONTACT_INFO['phoneExtension']


def test_add_contact_user_no_user(session):  # pylint: disable=unused-argument
    """Assert that a contact cannot be added to a user that does not exist."""
    with pytest.raises(BusinessException) as exception:
        UserService.add_contact(TEST_TOKEN, TEST_CONTACT_INFO)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_add_contact_to_user_already_exists(session):  # pylint: disable=unused-argument
    """Assert that a contact cannot be added to a user that already has a contact."""
    factory_user_model(username='testuser',
                       roles='{edit,uma_authorization,basic}',
                       keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    UserService.add_contact(TEST_TOKEN, TEST_CONTACT_INFO)

    with pytest.raises(BusinessException) as exception:
        UserService.add_contact(TEST_TOKEN, TEST_UPDATED_CONTACT_INFO)
    assert exception.value.code == Error.DATA_ALREADY_EXISTS.name


def test_update_contact_for_user(session):  # pylint: disable=unused-argument
    """Assert that a contact can be updated for a user."""
    factory_user_model(username='testuser',
                       roles='{edit,uma_authorization,basic}',
                       keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    user = UserService.add_contact(TEST_TOKEN, TEST_CONTACT_INFO)

    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['contacts']
    assert len(dictionary['contacts']) == 1

    updated_user = UserService.update_contact(TEST_TOKEN, TEST_UPDATED_CONTACT_INFO)

    assert updated_user is not None
    dictionary = updated_user.as_dict()
    assert dictionary['contacts'][0]['email'] == TEST_UPDATED_CONTACT_INFO['email']


def test_update_contact_for_user_no_user(session):  # pylint: disable=unused-argument
    """Assert that a contact cannot be updated for a user that does not exist."""
    with pytest.raises(BusinessException) as exception:
        UserService.update_contact(TEST_TOKEN, TEST_UPDATED_CONTACT_INFO)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_update_contact_for_user_no_contact(session):  # pylint: disable=unused-argument
    """Assert that a contact cannot be updated for a user with no contact."""
    factory_user_model(username='testuser',
                       roles='{edit,uma_authorization,basic}',
                       keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    with pytest.raises(BusinessException) as exception:
        UserService.update_contact(TEST_TOKEN, TEST_UPDATED_CONTACT_INFO)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_delete_contact_for_user(session):  # pylint: disable=unused-argument
    """Assert that a contact can be deleted for a user."""
    factory_user_model(username='testuser',
                       roles='{edit,uma_authorization,basic}',
                       keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    user = UserService.add_contact(TEST_TOKEN, TEST_CONTACT_INFO)

    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['contacts']
    assert len(dictionary['contacts']) == 1

    updated_user = UserService.delete_contact(TEST_TOKEN)

    assert updated_user is not None
    dictionary = updated_user.as_dict()
    assert dictionary.get('contacts') == []


def test_delete_contact_for_user_no_user(session):  # pylint: disable=unused-argument
    """Assert that deleting a contact for a non-existent user raises the right exception."""
    with pytest.raises(BusinessException) as exception:
        UserService.delete_contact(TEST_TOKEN)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_delete_contact_for_user_no_contact(session):  # pylint: disable=unused-argument
    """Assert that deleting a contact for a user with no contact raises the right exception."""
    factory_user_model(username='testuser',
                       roles='{edit,uma_authorization,basic}',
                       keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    with pytest.raises(BusinessException) as exception:
        UserService.delete_contact(TEST_TOKEN)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_find_users(session):  # pylint: disable=unused-argument
    """Assert that a list of users can be retrieved and searched on."""
    factory_user_model(username='testuser',
                       firstname='Test',
                       lastname='User',
                       roles='{edit,uma_authorization,basic}',
                       keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    factory_user_model(username='testuser2',
                       firstname='Test 2',
                       lastname='User',
                       roles='{edit,uma_authorization,basic}',
                       keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd05')

    users = UserService.find_users(last_name='User')
    assert users is not None
    assert len(users) == 2


def test_user_find_by_token(session):  # pylint: disable=unused-argument
    """Assert that a user can be found by token."""
    factory_user_model(username='testuser',
                       roles='{edit,uma_authorization,basic}',
                       keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    found_user = UserService.find_by_jwt_token(TEST_TOKEN)
    assert found_user is not None
    dictionary = found_user.as_dict()
    assert dictionary['username'] == TEST_TOKEN['preferred_username']
    assert dictionary['keycloak_guid'] == TEST_TOKEN['sub']


def test_user_find_by_username(session):  # pylint: disable=unused-argument
    """Assert that a user can be found by username."""
    user_model = factory_user_model(username='testuser',
                                    roles='{edit,uma_authorization,basic}',
                                    keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    user = UserService(user_model)

    user = UserService.find_by_username('testuser')

    assert user is not None
    dictionary = user.as_dict()
    assert dictionary['username'] == 'testuser'


def test_user_find_by_username_no_model_object(session):  # pylint: disable=unused-argument
    """Assert that the business can't be found with no model."""
    username = 'testuser'

    user = UserService.find_by_username(username)

    assert user is None


def test_user_find_by_username_missing_username(session):  # pylint: disable=unused-argument
    """Assert that the business can't be found by incorrect username."""
    user_model = factory_user_model(username='testuser',
                                    roles='{edit,uma_authorization,basic}',
                                    keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    user = UserService(user_model)

    user = UserService.find_by_username('foo')

    assert user is None


def test_get_orgs(session):  # pylint:disable=unused-argument
    """Assert that orgs for a user can be retrieved."""
    user_model = factory_user_model(username='testuser',
                                    roles='{edit,uma_authorization,basic}',
                                    keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    user = UserService(user_model)

    OrgService.create_org(TEST_ORG_INFO, user_id=user.identifier)

    response = user.get_orgs()
    assert response['orgs']
    assert len(response['orgs']) == 1
    assert response['orgs'][0]['name'] == TEST_ORG_INFO['name']

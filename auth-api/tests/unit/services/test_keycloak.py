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

"""Tests to assure the Business Service.

Test-Suite to ensure that the Business Service is working as expected.
"""

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.constants import GROUP_ACCOUNT_HOLDERS, GROUP_ANONYMOUS_USERS, GROUP_PUBLIC_USERS
from auth_api.utils.enums import LoginSource
from auth_api.utils.roles import Role
from tests.utilities.factory_scenarios import KeycloakScenario, TestJwtClaims
from tests.utilities.factory_utils import patch_token_info

KEYCLOAK_SERVICE = KeycloakService()


def test_keycloak_add_user(session):
    """Add user to Keycloak. Assert return a user with the same username as the username in request."""
    # with app.app_context():
    request = KeycloakScenario.create_user_request()
    user = KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    assert user.user_name == request.user_name


def test_keycloak_get_user_by_username(session):
    """Get user by username. Assert get a user with the same username as the username in request."""
    request = KeycloakScenario.create_user_request()
    # with app.app_context():
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    assert user.user_name == request.user_name


def test_keycloak_get_user_by_username_not_exist(session):
    """Get user by a username not exists in Keycloak. Assert user is None, error code is data not found."""
    user = None
    request = KeycloakScenario.create_user_request()
    # with app.app_context():
    try:
        user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    except BusinessException as err:
        assert err.code == Error.DATA_NOT_FOUND.name
    assert user is None


def test_keycloak_get_token(session):
    """Get token by username and password. Assert access_token is included in response."""
    request = KeycloakScenario.create_user_request()
    # with app.app_context():
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)

    response = KEYCLOAK_SERVICE.get_token(request.user_name, request.password)
    assert response.get('access_token') is not None
    KEYCLOAK_SERVICE.delete_user_by_username(request.user_name)


def test_keycloak_get_token_user_not_exist(session):
    """Get token by invalid username and password. Assert response is None, error is invalid user credentials."""
    response = None
    # with app.app_context():
    try:
        response = KEYCLOAK_SERVICE.get_token('test', 'test')
    except BusinessException as err:
        assert err.code == Error.INVALID_USER_CREDENTIALS.name
    assert response is None


def test_keycloak_delete_user_by_username(session):
    """Delete user by username.Assert response is not None."""
    # with app.app_context():
    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    KEYCLOAK_SERVICE.delete_user_by_username(request.user_name)
    assert True


def test_keycloak_delete_user_by_username_user_not_exist(session):
    """Delete user by invalid username. Assert response is None, error code data not found."""
    # with app.app_context():
    # First delete the user if it exists
    response = None
    try:
        response = KEYCLOAK_SERVICE.delete_user_by_username(KeycloakScenario.create_user_request().user_name)
    except BusinessException as err:
        assert err.code == Error.DATA_NOT_FOUND.name
    assert response is None


def test_join_users_group(app, session, monkeypatch):
    """Test the public_users group membership for public users."""
    # with app.app_context():
    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id

    patch_token_info({'sub': user_id, 'loginSource': LoginSource.BCSC.value,
                      'realm_access': {'roles': []}}, monkeypatch)
    KEYCLOAK_SERVICE.join_users_group()
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_PUBLIC_USERS in groups

    # BCROS
    patch_token_info({'sub': user_id, 'loginSource': LoginSource.BCROS.value, 'realm_access': {'roles': []}},
                     monkeypatch)
    KEYCLOAK_SERVICE.join_users_group()
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ANONYMOUS_USERS in groups


def test_join_users_group_for_staff_users(session, app, monkeypatch):
    """Test the staff user account creation, and assert the public_users group is not added."""
    # with app.app_context():
    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id
    patch_token_info({'sub': user_id, 'loginSource': LoginSource.STAFF.value, 'realm_access': {'roles': []}},
                     monkeypatch)
    KEYCLOAK_SERVICE.join_users_group()
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_PUBLIC_USERS not in groups


def test_join_users_group_for_existing_users(session, monkeypatch):
    """Test the existing user account, and assert the public_users group is not added."""
    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id

    patch_token_info(
        {'sub': user_id, 'loginSource': LoginSource.BCSC.value, 'realm_access': {'roles': [Role.EDITOR.value]}},
        monkeypatch)
    KEYCLOAK_SERVICE.join_users_group()
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_PUBLIC_USERS in groups


def test_join_account_holders_group(session):
    """Assert that the account_holders group is getting added to the user."""
    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id
    KEYCLOAK_SERVICE.join_account_holders_group(keycloak_guid=user_id)
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups


def test_join_account_holders_group_from_token(session, monkeypatch):
    """Assert that the account_holders group is getting added to the user."""
    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id

    # Patch token info
    patch_token_info({'sub': user_id}, monkeypatch)

    KEYCLOAK_SERVICE.join_account_holders_group()
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups


def test_remove_from_account_holders_group(session, monkeypatch):
    """Assert that the account_holders group is removed from the user."""
    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id
    KEYCLOAK_SERVICE.join_account_holders_group(keycloak_guid=user_id)
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups
    patch_token_info(TestJwtClaims.gov_account_holder_user, monkeypatch)
    KEYCLOAK_SERVICE.remove_from_account_holders_group(keycloak_guid=user_id)
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS not in groups


def test_reset_otp(session):
    """Assert that the user otp configuration get reset in keycloak."""
    request = KeycloakScenario.create_user_by_user_info(user_info=TestJwtClaims.tester_bceid_role)
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id
    KEYCLOAK_SERVICE.reset_otp(user_id)
    assert True

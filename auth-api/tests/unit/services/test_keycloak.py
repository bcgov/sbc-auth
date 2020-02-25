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
from auth_api.services.keycloak import KeycloakConfig, KeycloakService
from auth_api.utils.constants import GROUP_ACCOUNT_HOLDERS, GROUP_PUBLIC_USERS, PASSCODE, STAFF
from auth_api.utils.roles import Role


ADD_USER_REQUEST = {
    'username': 'test11',
    'password': '1111',
    'firstname': '111',
    'lastname': 'test',
    'email': 'test11@gov.bc.ca',
    'enabled': True,
    'user_type': [
        '/test'
    ],
    'corp_type': 'CP',
    'source': PASSCODE
}

ADD_USER_REQUEST_SAME_EMAIL = {
    'username': 'test12',
    'password': '1111',
    'firstname': '112',
    'lastname': 'test',
    'email': 'test11@gov.bc.ca',
    'enabled': True,
    'user_type': [
        '/test',
        '/basic/editor'
    ],
    'corp_type': 'CP',
    'source': PASSCODE
}

KEYCLOAK_SERVICE = KeycloakService()


def test_keycloak_add_user(app):
    """Add user to Keycloak. Assert return a user with the same username as the username in request."""
    with app.app_context():
        user = KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
        assert user.get('username') == ADD_USER_REQUEST.get('username')
        KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_add_user_duplicate_email():
    """Add user with duplicate email. Assert response is None, error code is data conflict."""
    # First delete the user if it exists
    try:
        if KEYCLOAK_SERVICE.get_user_by_username(ADD_USER_REQUEST.get('username')):
            KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))
    except Exception:
        pass

    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    try:
        KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST_SAME_EMAIL)
    except BusinessException as err:
        assert err.code == Error.DATA_CONFLICT.name
    finally:
        KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_get_user_by_username():
    """Get user by username. Assert get a user with the same username as the username in request."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    user = KEYCLOAK_SERVICE.get_user_by_username(ADD_USER_REQUEST.get('username'))
    assert user.get('username') == ADD_USER_REQUEST.get('username')
    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_get_user_by_username_not_exist():
    """Get user by a username not exists in Keycloak. Assert user is None, error code is data not found."""
    user = None
    try:
        user = KEYCLOAK_SERVICE.get_user_by_username(ADD_USER_REQUEST.get('username'))
    except BusinessException as err:
        assert err.code == Error.DATA_NOT_FOUND.name
    assert user is None


def test_keycloak_get_token():
    """Get token by username and password. Assert access_token is included in response."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    response = KEYCLOAK_SERVICE.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    assert response.get('access_token') is not None
    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_get_token_user_not_exist():
    """Get token by invalid username and password. Assert response is None, error is invalid user credentials."""
    response = None
    try:
        response = KEYCLOAK_SERVICE.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    except BusinessException as err:
        assert err.code == Error.INVALID_USER_CREDENTIALS.name
    assert response is None


def test_keycloak_refresh_token():
    """Refresh token. Assert access_token is included in response."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    response = KEYCLOAK_SERVICE.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    refresh_token = response.get('refresh_token')
    response = KEYCLOAK_SERVICE.refresh_token(refresh_token)

    assert response.get('access_token') is not None
    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_refresh_token_wrong_refresh_token():
    """Refresh token by invalid refresh token. Assert response is None, error code is invalid refresh token."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    response = KEYCLOAK_SERVICE.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    refresh_token = response.get('access_token')
    response = None
    try:
        response = KEYCLOAK_SERVICE.refresh_token(refresh_token)
    except BusinessException as err:
        assert err.code == Error.INVALID_REFRESH_TOKEN.name
    assert response is None
    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_delete_user_by_username():
    """Delete user by username.Assert response is not None."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    response = KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))
    assert response is not None


def test_keycloak_delete_user_by_username_user_not_exist():
    """Delete user by invalid username. Assert response is None, error code data not found."""
    # First delete the user if it exists
    try:
        if KEYCLOAK_SERVICE.get_user_by_username(ADD_USER_REQUEST_SAME_EMAIL.get('username')):
            KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST_SAME_EMAIL.get('username'))
    except Exception:
        pass

    response = None
    try:
        response = KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST_SAME_EMAIL.get('username'))
    except BusinessException as err:
        assert err.code == Error.DATA_NOT_FOUND.name
    assert response is None


def test_keycloak_logout(session):
    """Logout. Assert response status code is included in response."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    response = KEYCLOAK_SERVICE.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    refresh_token = response.get('refresh_token')
    response = KEYCLOAK_SERVICE.logout(refresh_token)

    assert response is not None
    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_logout_wrong_refresh_token(session):
    """Logout by invalid refresh token. Assert response is None, error code is invalid refresh token."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    response = KEYCLOAK_SERVICE.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    refresh_token = response.get('access_token')
    response = None
    try:
        response = KEYCLOAK_SERVICE.logout(refresh_token)
    except BusinessException as err:
        assert err.code == Error.INVALID_REFRESH_TOKEN.name
        pass
    assert response is None
    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_join_public_users_group(app, session):
    """Test the public_users group membership for public users."""
    with app.app_context():
        KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
        user = KEYCLOAK_SERVICE.get_user_by_username(ADD_USER_REQUEST.get('username'))
        user_id = user.get('id')
        KEYCLOAK_SERVICE.join_public_users_group({'sub': user_id,
                                                  'loginSource': PASSCODE,
                                                  'realm_access': {'roles': []}})
        # Get the user groups and verify the public_users group is in the list
        user_groups = KeycloakConfig().get_keycloak_admin().get_user_groups(user_id=user_id)
        groups = []
        for group in user_groups:
            groups.append(group.get('name'))
        assert GROUP_PUBLIC_USERS in groups

        KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_join_public_users_group_for_staff_users(session):
    """Test the staff user account creation, and assert the public_users group is not added."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    user = KEYCLOAK_SERVICE.get_user_by_username(ADD_USER_REQUEST.get('username'))
    user_id = user.get('id')
    KEYCLOAK_SERVICE.join_public_users_group({'sub': user_id, 'loginSource': STAFF, 'realm_access': {'roles': []}})
    # Get the user groups and verify the public_users group is in the list
    user_groups = KeycloakConfig().get_keycloak_admin().get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_PUBLIC_USERS not in groups

    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_join_public_users_group_for_existing_users(session):
    """Test the existing user account, and assert the public_users group is not added."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    user = KEYCLOAK_SERVICE.get_user_by_username(ADD_USER_REQUEST.get('username'))
    user_id = user.get('id')
    KEYCLOAK_SERVICE.join_public_users_group(
        {'sub': user_id, 'loginSource': PASSCODE, 'realm_access': {'roles': [Role.EDITOR.value]}})
    # Get the user groups and verify the public_users group is in the list
    user_groups = KeycloakConfig().get_keycloak_admin().get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_PUBLIC_USERS not in groups

    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_join_account_holders_group(session):
    """Assert that the account_holders group is getting added to the user."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    user = KEYCLOAK_SERVICE.get_user_by_username(ADD_USER_REQUEST.get('username'))
    user_id = user.get('id')
    KEYCLOAK_SERVICE.join_account_holders_group(keycloak_guid=user_id)
    # Get the user groups and verify the public_users group is in the list
    user_groups = KeycloakConfig().get_keycloak_admin().get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups

    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_join_account_holders_group_from_token(session, monkeypatch):
    """Assert that the account_holders group is getting added to the user."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    user = KEYCLOAK_SERVICE.get_user_by_username(ADD_USER_REQUEST.get('username'))
    user_id = user.get('id')

    # Patch token info
    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {
            'sub': str(user_id),
            'username': 'public user',
            'realm_access': {
                'roles': [
                ]
            }
        }

    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService._get_token_info', token_info)

    KEYCLOAK_SERVICE.join_account_holders_group()
    # Get the user groups and verify the public_users group is in the list
    user_groups = KeycloakConfig().get_keycloak_admin().get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups

    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_remove_from_account_holders_group(session):
    """Assert that the account_holders group is removed from the user."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    user = KEYCLOAK_SERVICE.get_user_by_username(ADD_USER_REQUEST.get('username'))
    user_id = user.get('id')
    KEYCLOAK_SERVICE.join_account_holders_group(keycloak_guid=user_id)
    # Get the user groups and verify the public_users group is in the list
    user_groups = KeycloakConfig().get_keycloak_admin().get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups
    KEYCLOAK_SERVICE.remove_from_account_holders_group(keycloak_guid=user_id)
    user_groups = KeycloakConfig().get_keycloak_admin().get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS not in groups

    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))

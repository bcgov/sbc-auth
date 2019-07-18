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


ADD_USER_REQUEST = {
    'username': 'test11',
    'password': '1111',
    'firstname': '111',
    'lastname': 'test',
    'email': 'test11@gov.bc.ca',
    'enabled': True,
    'user_type': [
        '/test',
        '/basic/editor'
    ],
    'corp_type': 'CP',
    'source': 'PASSCODE'
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
    'source': 'PASSCODE'
}


KEYCLOAK_SERVICE = KeycloakService()


def test_keycloak_add_user():
    """Add user to Keycloak. Assert return a user with the same username as the username in request."""
    user = KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    assert user.get('username') == ADD_USER_REQUEST.get('username')
    KEYCLOAK_SERVICE.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_add_user_duplicate_email():
    """Add user with duplicate email. Assert response is None, error code is data conflict."""
    KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST)
    response = None
    try:
        response = KEYCLOAK_SERVICE.add_user(ADD_USER_REQUEST_SAME_EMAIL)
    except BusinessException as err:
        assert err.code == Error.DATA_CONFLICT.name
    assert response is None
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
    response = None
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

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


keycloak_service = KeycloakService()


def test_keycloak_add_user(session):
    """Add user to Keycloak. Assert return a user with the same username as the username in request."""
    user = keycloak_service.add_user(ADD_USER_REQUEST)
    assert user.get('username') == ADD_USER_REQUEST.get('username')
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_add_user_duplicate_email(session):
    """Add user with duplicate email. Assert response is None."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    response = None
    try:
        response = keycloak_service.add_user(ADD_USER_REQUEST_SAME_EMAIL)
    except Exception as err:
        pass
    assert response is None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_get_user_by_username(session):
    """Get user by username. Assert get a user with the same username as the username in request."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    user = keycloak_service.get_user_by_username(ADD_USER_REQUEST.get('username'))
    assert user.get('username') == ADD_USER_REQUEST.get('username')
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_get_user_by_username_not_exist(session):
    """Get user by a username not exists in Keycloak. Assert user is None."""
    user = None
    try:
        user = keycloak_service.get_user_by_username(ADD_USER_REQUEST.get('username'))
    except Exception as err:
        pass
    assert user is None


def test_keycloak_get_token(session):
    """Get token by username and password. Assert access_token is included in response."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    response = keycloak_service.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    assert response.get('access_token') is not None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_get_token_user_not_exist(session):
    """Get token by invalid username and password. Assert response is None."""
    response = None
    try:
        response = keycloak_service.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    except Exception as err:
        pass
    assert response is None


def test_keycloak_refresh_token(session):
    """Refresh token. Assert access_token is included in response."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    response = keycloak_service.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    refresh_token = response.get('refresh_token')
    response = keycloak_service.refresh_token(refresh_token)
    assert response.get('access_token') is not None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_refresh_token_wrong_refresh_token(session):
    """Refresh token by invalid refresh token. Assert response is None."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    response = keycloak_service.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    refresh_token = response.get('access_token')
    response = None
    try:
        response = keycloak_service.refresh_token(refresh_token)
    except Exception as err:
        pass
    assert response is None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_delete_user_by_username(session):
    """Delete user by username.Assert response is not None."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    response = keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))
    assert response is not None


def test_keycloak_delete_user_by_username_user_not_exist(session):
    """Delete user by invalid username. Assert response is None."""
    response = None
    try:
        response = keycloak_service.delete_user_by_username(ADD_USER_REQUEST_SAME_EMAIL.get('username'))
    except Exception as err:
        pass
    assert response is None

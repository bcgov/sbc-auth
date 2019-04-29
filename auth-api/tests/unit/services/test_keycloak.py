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
import json
from auth_api.services.keycloak import KeycloakService

ADD_USER_REQUEST = {
   "username": "test11",
   "password": "1111",
   "firstname": "111",
   "lastname": "test",
   "email": "test11@gov.bc.ca",
   "enabled": True,
   "user_type": [
       "/test",
       "/basic/editor"
   ],
   "corp_type": "CP",
   "source": "PASSCODE"
}

ADD_USER_REQUEST_SAME_EMAIL = {
   "username": "test12",
   "password": "1111",
   "firstname": "112",
   "lastname": "test",
   "email": "test11@gov.bc.ca",
   "enabled": True,
   "user_type": [
       "/test",
       "/basic/editor"
   ],
   "corp_type": "CP",
   "source": "PASSCODE"
}

keycloak_service = KeycloakService()


def test_keycloak_add_user_happy(session):
    """add user happy path"""
    user = keycloak_service.add_user(ADD_USER_REQUEST)
    assert user.get('username') == 'test11'
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get("username"))


def test_keycloak_add_user_sad(session):
    """add user sad path"""
    user = keycloak_service.add_user(ADD_USER_REQUEST)
    response = None
    try:
        response = keycloak_service.add_user(ADD_USER_REQUEST_SAME_EMAIL)
    except Exception as err:
        pass
    assert response is None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get("username"))


def test_keycloak_get_user_by_username_happy(session):
    """get user by username happy path"""
    user = keycloak_service.add_user(ADD_USER_REQUEST)
    user = keycloak_service.get_user_by_username(ADD_USER_REQUEST.get("username"))
    assert user.get('username') == 'test11'
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get("username"))


def test_keycloak_get_user_by_username_sad(session):
    """get user by username sad path"""
    user = None
    try:
        user = keycloak_service.get_user_by_username(ADD_USER_REQUEST.get("username"))
    except Exception as err:
        pass
    assert user is None


def test_keycloak_get_token_happy(session):
    """get token by username and password happy path"""
    user = keycloak_service.add_user(ADD_USER_REQUEST)
    response = keycloak_service.get_token(ADD_USER_REQUEST.get("username"), ADD_USER_REQUEST.get("password"))
    assert response.get('access_token') is not None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get("username"))


def test_keycloak_get_token_sad(session):
    """get token by username and password sad path"""
    user = None
    try:
        user = keycloak_service.get_token(ADD_USER_REQUEST.get("username"), ADD_USER_REQUEST.get("password"))
    except Exception as err:
        pass
    assert user is None


def test_keycloak_refresh_token_happy(session):
    """Refresh token happy path"""
    user = keycloak_service.add_user(ADD_USER_REQUEST)
    response = keycloak_service.get_token(ADD_USER_REQUEST.get("username"), ADD_USER_REQUEST.get("password"))
    refresh_token = response.get('refresh_token')
    response = keycloak_service.refresh_token(refresh_token)
    assert response.get('access_token') is not None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get("username"))


def test_keycloak_refresh_token_sad(session):
    """Refresh token sad path"""
    user = keycloak_service.add_user(ADD_USER_REQUEST)
    response = keycloak_service.get_token(ADD_USER_REQUEST.get("username"), ADD_USER_REQUEST.get("password"))
    refresh_token = response.get('access_token')
    response = None
    try:
        response = keycloak_service.refresh_token(refresh_token)
    except Exception as err:
        pass
    assert response is None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get("username"))


def test_keycloak_delete_user_by_username_happy(session):
    """Delete user by username happy path"""
    user = keycloak_service.add_user(ADD_USER_REQUEST)
    response = keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get("username"))
    assert response is not None



def test_keycloak_delete_user_by_username_sad(session):
    """Delete user by username sad path"""
    user = keycloak_service.add_user(ADD_USER_REQUEST)
    response = None
    try:
        response = keycloak_service.delete_user_by_username(ADD_USER_REQUEST_SAME_EMAIL.get("username"))
    except Exception as err:
        pass
    assert response is None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get("username"))


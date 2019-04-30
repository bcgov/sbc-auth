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

from unittest.mock import Mock, patch
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

ADD_USER_RESPONSE = {
    "id": "79f30e30-02f8-4fec-a48f-b80b465bc081",
    "createdTimestamp": 1556646546660,
    "username": "test11",
    "enabled": True,
    "totp": False,
    "emailVerified": False,
    "firstName": "111",
    "lastName": "test",
    "email": "test11@gov.bc.ca",
    "attributes": {
        "corp_type": [
            "CP"
        ],
        "source": [
            "PASSCODE"
        ]
    },
    "disableableCredentialTypes": [
        "password"
    ],
    "requiredActions": [],
    "federatedIdentities": [],
    "notBefore": 0,
    "access": {
        "manageGroupMembership": True,
        "view": True,
        "mapRoles": True,
        "impersonate": True,
        "manage": True
    }
}

keycloak_service = KeycloakService()


def test_keycloak_add_user(session):
    """Add user happy path."""
    user = keycloak_service.add_user(ADD_USER_REQUEST)
    assert user.get('username') == 'test11'
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_add_user_duplicate_email(session):
    """Add user sad path."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    response = None
    try:
        response = keycloak_service.add_user(ADD_USER_REQUEST_SAME_EMAIL)
    except Exception as err:
        pass
    assert response is None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_get_user_by_username(session):
    """Get user by username happy path."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    user = keycloak_service.get_user_by_username(ADD_USER_REQUEST.get('username'))
    assert user.get('username') == 'test11'
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_get_user_by_username_not_exist(session):
    """Get user by username sad path."""
    user = None
    try:
        user = keycloak_service.get_user_by_username(ADD_USER_REQUEST.get('username'))
    except Exception as err:
        pass
    assert user is None


def test_keycloak_get_token(session):
    """Get token by username and password happy path."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    response = keycloak_service.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    assert response.get('access_token') is not None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_get_token_user_not_exist(session):
    """Get token by username and password sad path."""
    user = None
    try:
        user = keycloak_service.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    except Exception as err:
        pass
    assert user is None


def test_keycloak_refresh_token(session):
    """Refresh token happy path."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    response = keycloak_service.get_token(ADD_USER_REQUEST.get('username'), ADD_USER_REQUEST.get('password'))
    refresh_token = response.get('refresh_token')
    response = keycloak_service.refresh_token(refresh_token)
    assert response.get('access_token') is not None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))


def test_keycloak_refresh_token_wrong_refresh_token(session):
    """Refresh token sad path."""
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
    """Delete user by username happy path."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    response = keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))
    assert response is not None


def test_keycloak_delete_user_by_username_user_not_exist(session):
    """Delete user by username sad path."""
    keycloak_service.add_user(ADD_USER_REQUEST)
    response = None
    try:
        response = keycloak_service.delete_user_by_username(ADD_USER_REQUEST_SAME_EMAIL.get('username'))
    except Exception as err:
        pass
    assert response is None
    keycloak_service.delete_user_by_username(ADD_USER_REQUEST.get('username'))

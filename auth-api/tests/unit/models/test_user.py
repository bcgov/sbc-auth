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

"""Tests to assure the User Class.

Test-Suite to ensure that the User Class is working as expected.
"""

from auth_api.models import User


def test_user(session):
    """Assert that a User can be stored in the service.

    Start with a blank database.
    """
    user = User(username='CP1234567',
                roles='{edit, uma_authorization, staff}',
                keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    session.add(user)
    session.commit()

    assert user.id is not None


def test_user_find_by_jwt_token(session):
    """Assert that a User can be stored in the service.

    Start with a blank database.
    """
    user = User(username='CP1234567',
                roles='{edit, uma_authorization, staff}',
                keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    session.add(user)
    session.commit()

    token = {
        'preferred_username': 'CP1234567',
        'sub': '1b20db59-19a0-4727-affe-c6f64309fd04',
        'realm_access': {
            'roles': [
                'edit',
                'uma_authorization',
                'basic'
            ]
        }
    }
    u = User.find_by_jwt_token(token)

    assert u.id is not None


def test_create_from_jwt_token(session):  # pylint: disable=unused-argument
    """Assert User is created from the JWT fields."""
    token = {
        'preferred_username': 'CP1234567',
        'realm_access': {
            'roles': [
                'edit',
                'uma_authorization',
                'basic'
                ]
            },
        'sub': '1b20db59-19a0-4727-affe-c6f64309fd04'
    }
    u = User.create_from_jwt_token(token)
    assert u.id is not None


def test_create_from_jwt_token_no_token(session):  # pylint: disable=unused-argument
    """Assert User is not created from an empty token."""
    token = None
    u = User.create_from_jwt_token(token)
    assert u is None


def test_update_from_jwt_token(session):  # pylint: disable=unused-argument
    """Assert User is updated from a JWT and an existing User model."""
    token = {
        'preferred_username': 'CP1234567',
        'firstname': 'Bobby',
        'lasname': 'Joe',
        'realm_access': {
            'roles': [
                'edit',
                'uma_authorization',
                'basic'
                ]
            },
        'sub': '1b20db59-19a0-4727-affe-c6f64309fd04'
    }
    user = User.create_from_jwt_token(token)

    updated_token = {
        'preferred_username': 'CP1234567',
        'firstname': 'Bob',
        'lastname': 'Joe',
        'realm_access': {
            'roles': [
                'edit',
                'uma_authorization',
                'basic'
                ]
            },
        'sub': '1b20db59-19a0-4727-affe-c6f64309fd04'
    }
    user = User.update_from_jwt_token(updated_token, user)

    assert user.firstname == 'Bob'


def test_update_from_jwt_token_no_token(session):  # pylint:disable=unused-argument
    """Assert that a user is not updateable without a token (should return None)."""
    token = {
        'preferred_username': 'CP1234567',
        'firstname': 'Bobby',
        'lasname': 'Joe',
        'realm_access': {
            'roles': [
                'edit',
                'uma_authorization',
                'basic'
                ]
            },
        'sub': '1b20db59-19a0-4727-affe-c6f64309fd04'
    }
    existing_user = User.create_from_jwt_token(token)

    token = None
    user = User.update_from_jwt_token(token, existing_user)
    assert user is None


def test_find_by_username(session):
    """Assert User can be found by the most current username."""
    user = User(username='CP1234567',
                roles='{edit, uma_authorization, staff}',
                keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    session.add(user)
    session.commit()

    u = User.find_by_username('CP1234567')

    assert u.id is not None


def test_user_save(session):  # pylint: disable=unused-argument
    """Assert User record is saved."""
    user = User(username='CP1234567',
                roles='{edit, uma_authorization, staff}',
                keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    user.save()

    assert user.id is not None


def test_user_delete(session):  # pylint: disable=unused-argument
    """Assert the User record is deleted."""
    user = User(username='CP1234567',
                roles='{edit, uma_authorization, staff}',
                keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    user.save()
    user.delete()

    assert user.id is not None

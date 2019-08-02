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

from auth_api import services


def factory_user_model(username,
                       roles,
                       keycloak_guid):
    """Return a valid user object stamped with the supplied designation."""
    from auth_api.models import User as UserModel
    user = UserModel(username=username,
                     roles=roles,
                     keycloak_guid=keycloak_guid)
    user.save()
    return user


def test_as_dict():
    """Assert that the User is rendered correctly as a dict."""
    user = services.User()
    user.username = 'CP1234567'
    user.roles = '{edit,uma_authorization,basic}'

    assert user.asdict() == {'username': 'CP1234567', 'roles': '{edit,uma_authorization,basic}'}


def test_user_saved_from_new(session):  # pylint: disable=unused-argument
    """Assert that the business is saved to the cache."""
    username = 'CP1234567'
    user = services.User()
    user.username = username
    user.roles = '{edit,uma_authorization,basic}'
    user.keycloak_guid = '1b20db59-19a0-4727-affe-c6f64309fd04'
    user.save()

    user = services.User.find_by_username(username)

    assert user is not None


def test_user_retrieved_from_cache(session):  # pylint: disable=unused-argument
    """Assert that the business is saved to the cache."""
    username = 'CP1234567'
    factory_user_model(username=username,
                       roles='{edit,uma_authorization,basic}',
                       keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    user = services.User.find_by_username(username)

    alt_roles = '{edit,uma_authorization,staff}'
    user.roles = alt_roles
    user.save()

    user = services.User.find_by_username(username)

    assert user.roles == alt_roles


def test_user_find_by_username(session):  # pylint: disable=unused-argument
    """Assert that the business can be found by name."""
    username = 'CP1234567'
    user = services.User()
    user.roles = '{edit,uma_authorization,basic}'
    user.username = username
    user.keycloak_guid = '1b20db59-19a0-4727-affe-c6f64309fd04'
    user.save()

    user = services.User.find_by_username(username)

    assert user is not None


def test_user_find_by_username_no_model_object(session):  # pylint: disable=unused-argument
    """Assert that the business can't be found with no model."""
    username = 'CP1234567'

    user = services.User.find_by_username(username)

    assert user is None


def test_user_find_by_username_missing_username(session):  # pylint: disable=unused-argument
    """Assert that the business can be found by name."""
    username = 'CP1234567'
    user = services.User()
    user.roles = '{edit,uma_authorization,basic}'
    user.username = username
    user.keycloak_guid = '1b20db59-19a0-4727-affe-c6f64309fd04'
    user.save()

    user = services.User.find_by_username(None)

    assert user is None

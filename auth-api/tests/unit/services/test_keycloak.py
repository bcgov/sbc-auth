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

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.dataclass import KeycloakGroupSubscription
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.constants import GROUP_ACCOUNT_HOLDERS, GROUP_ANONYMOUS_USERS, GROUP_PUBLIC_USERS
from auth_api.utils.enums import KeycloakGroupActions, LoginSource
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
    assert response.get("access_token") is not None
    KEYCLOAK_SERVICE.delete_user_by_username(request.user_name)


def test_keycloak_get_token_user_not_exist(session):
    """Get token by invalid username and password. Assert response is None, error is invalid user credentials."""
    response = None
    # with app.app_context():
    try:
        response = KEYCLOAK_SERVICE.get_token("test", "test")
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

    patch_token_info(
        {"sub": user_id, "loginSource": LoginSource.BCSC.value, "realm_access": {"roles": []}}, monkeypatch
    )
    KEYCLOAK_SERVICE.join_users_group()
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get("name"))
    assert GROUP_PUBLIC_USERS in groups

    # BCROS
    patch_token_info(
        {"sub": user_id, "loginSource": LoginSource.BCROS.value, "realm_access": {"roles": []}}, monkeypatch
    )
    KEYCLOAK_SERVICE.join_users_group()
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get("name"))
    assert GROUP_ANONYMOUS_USERS in groups


def test_join_users_group_for_staff_users(session, app, monkeypatch):
    """Test the staff user account creation, and assert the public_users group is not added."""
    # with app.app_context():
    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id
    patch_token_info(
        {"sub": user_id, "loginSource": LoginSource.STAFF.value, "realm_access": {"roles": []}}, monkeypatch
    )
    KEYCLOAK_SERVICE.join_users_group()
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get("name"))
    assert GROUP_PUBLIC_USERS not in groups


def test_join_users_group_for_existing_users(session, monkeypatch):
    """Test the existing user account, and assert the public_users group is not added."""
    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id

    patch_token_info(
        {"sub": user_id, "loginSource": LoginSource.BCSC.value, "realm_access": {"roles": [Role.EDITOR.value]}},
        monkeypatch,
    )
    KEYCLOAK_SERVICE.join_users_group()
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get("name"))
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
        groups.append(group.get("name"))
    assert GROUP_ACCOUNT_HOLDERS in groups


def test_join_account_holders_group_from_token(session, monkeypatch):
    """Assert that the account_holders group is getting added to the user."""
    request = KeycloakScenario.create_user_request()
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id

    # Patch token info
    patch_token_info({"sub": user_id}, monkeypatch)

    KEYCLOAK_SERVICE.join_account_holders_group()
    # Get the user groups and verify the public_users group is in the list
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get("name"))
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
        groups.append(group.get("name"))
    assert GROUP_ACCOUNT_HOLDERS in groups
    patch_token_info(TestJwtClaims.gov_account_holder_user, monkeypatch)
    KEYCLOAK_SERVICE.remove_from_account_holders_group(keycloak_guid=user_id)
    user_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user_id)
    groups = []
    for group in user_groups:
        groups.append(group.get("name"))
    assert GROUP_ACCOUNT_HOLDERS not in groups


def test_reset_otp(session):
    """Assert that the user otp configuration get reset in keycloak."""
    request = KeycloakScenario.create_user_by_user_info(user_info=TestJwtClaims.tester_bceid_role)
    KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    user_id = user.id
    KEYCLOAK_SERVICE.reset_otp(user_id)
    assert True


@pytest.mark.asyncio
def test_add_remove_group_bulk(session):
    """Assert that the users' groups can be updated in bulk."""
    user1 = KEYCLOAK_SERVICE.add_user(KeycloakScenario.create_user_request(), return_if_exists=True)
    user2 = KEYCLOAK_SERVICE.add_user(KeycloakScenario.create_user_request(), return_if_exists=True)
    kgs = [
        KeycloakGroupSubscription(
            user_guid=user1.id,
            product_code="ppr",
            group_name="ppr",
            group_action=KeycloakGroupActions.ADD_TO_GROUP.value,
        ),
        KeycloakGroupSubscription(
            user_guid=user2.id,
            product_code="bca",
            group_name="bca",
            group_action=KeycloakGroupActions.ADD_TO_GROUP.value,
        ),
        KeycloakGroupSubscription(
            user_guid=user2.id,
            product_code="bca",
            group_name="bca",
            group_action=KeycloakGroupActions.REMOVE_FROM_GROUP.value,
        ),
    ]
    KeycloakService.add_or_remove_product_keycloak_groups(kgs)
    user1_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user1.id)
    user2_groups = KEYCLOAK_SERVICE.get_user_groups(user_id=user2.id)
    assert "ppr" in ["ppr" for user_group in user1_groups if user_group.get("name") == "ppr"]
    assert "bca" not in ["bca" for user_group in user2_groups if user_group.get("name") == "bca"]


def test_service_account_by_client_name(session):
    """Test keycloak service account by client name."""
    result = KeycloakService.get_service_account_by_client_name("sbc-auth-admin")
    assert result is not None
    assert result.get("username") == "service-account-sbc-auth-admin"
    assert result.get("id") is not None


@patch("auth_api.services.keycloak.KeycloakService._get_admin_token")
@patch("auth_api.services.keycloak.KeycloakService.get_keycloak_users_for_role")
@patch("auth_api.services.keycloak.KeycloakService.get_keycloak_groups_for_role")
@patch("auth_api.services.keycloak.KeycloakService.get_keycloak_members_for_group")
def test_get_user_emails_with_role(
    mock_get_group_members,
    mock_get_groups_for_role,
    mock_get_users_for_role,
    mock_get_admin_token,
    session,
):
    """Test get_user_emails_with_role returns users from both direct role assignment and group membership."""
    mock_get_admin_token.return_value = "mock_token"

    # Set up for direct role assignment to a user and test handling logic when users are returned
    kc_users = [
        {"id": "user1", "firstName": "John", "lastName": "Doe", "email": "john.doe@example.com"},
        {"id": "user2", "firstName": "Jane", "lastName": "Smith", "email": "jane.smith@example.com"},
    ]

    # Groups and group members to test logic when inherited group roles exist
    kc_groups = [{"id": "group1", "name": "test_group_1"}, {"id": "group2", "name": "test_group_2"}]

    group1_members = [
        {"id": "user3", "firstName": "Bob", "lastName": "Johnson", "email": "bob.johnson@example.com"},
        {"id": "user1", "firstName": "John", "lastName": "Doe", "email": "john.doe@example.com"},
    ]

    group2_members = [{"id": "user4", "firstName": "Alice", "lastName": "Brown", "email": "alice.brown@example.com"}]
    mock_get_users_for_role.return_value = kc_users
    mock_get_groups_for_role.return_value = kc_groups

    def mock_get_members(group_id):
        if group_id == "group1":
            return group1_members
        elif group_id == "group2":
            return group2_members
        return []

    mock_get_group_members.side_effect = mock_get_members

    result = KEYCLOAK_SERVICE.get_user_emails_with_role("test_role")

    mock_get_users_for_role.assert_called_once_with("test_role")
    mock_get_groups_for_role.assert_called_once_with("test_role")
    assert mock_get_group_members.call_count == 2
    mock_get_group_members.assert_any_call("group1")
    mock_get_group_members.assert_any_call("group2")
    assert len(result) == 5

    emails = [user["email"] for user in result]
    expected_emails = [
        "john.doe@example.com",
        "jane.smith@example.com",
        "bob.johnson@example.com",
        "alice.brown@example.com",
    ]

    for email in expected_emails:
        assert email in emails

    for user in result:
        assert "firstName" in user
        assert "lastName" in user
        assert "email" in user
        assert len(user) == 3


@patch("auth_api.services.keycloak.KeycloakService._get_admin_token")
@patch("auth_api.services.keycloak.KeycloakService.get_keycloak_users_for_role")
@patch("auth_api.services.keycloak.KeycloakService.get_keycloak_groups_for_role")
@patch("auth_api.services.keycloak.KeycloakService.get_keycloak_members_for_group")
def test_get_user_emails_with_role_empty_results(
    mock_get_group_members,
    mock_get_groups_for_role,
    mock_get_users_for_role,
    mock_get_admin_token,
    session,
):
    """Test get_user_emails_with_role handles empty results correctly."""
    mock_get_admin_token.return_value = "mock_token"
    mock_get_users_for_role.return_value = []
    mock_get_groups_for_role.return_value = []
    result = KEYCLOAK_SERVICE.get_user_emails_with_role("nonexistent_role")

    assert result == []

    mock_get_users_for_role.assert_called_once_with("nonexistent_role")
    mock_get_groups_for_role.assert_called_once_with("nonexistent_role")
    mock_get_group_members.assert_not_called()


@patch("auth_api.services.keycloak.KeycloakService._get_admin_token")
@patch("auth_api.services.keycloak.KeycloakService.get_keycloak_users_for_role")
@patch("auth_api.services.keycloak.KeycloakService.get_keycloak_groups_for_role")
@patch("auth_api.services.keycloak.KeycloakService.get_keycloak_members_for_group")
def test_get_user_emails_with_role_none_users(
    mock_get_group_members,
    mock_get_groups_for_role,
    mock_get_users_for_role,
    mock_get_admin_token,
    session,
):
    """Test get_user_emails_with_role handles None return from get_keycloak_users_for_role."""
    mock_get_admin_token.return_value = "mock_token"
    mock_get_users_for_role.return_value = None

    role_groups = [{"id": "group1", "name": "test_group"}]
    mock_get_groups_for_role.return_value = role_groups

    group_members = [{"id": "user1", "firstName": "Test", "lastName": "User", "email": "test.user@example.com"}]
    mock_get_group_members.return_value = group_members
    result = KEYCLOAK_SERVICE.get_user_emails_with_role("test_role")

    assert len(result) == 1
    assert result[0]["email"] == "test.user@example.com"
    assert result[0]["firstName"] == "Test"
    assert result[0]["lastName"] == "User"


@patch("auth_api.services.keycloak.KeycloakService._get_admin_token")
@patch("auth_api.services.keycloak.KeycloakService.get_keycloak_users_for_role")
def test_get_user_emails_with_role_nonexistent_role(
    mock_get_users_for_role,
    mock_get_admin_token,
    session,
):
    """Test get_user_emails_with_role raises BusinessException when role doesn't exist in Keycloak."""
    mock_get_admin_token.return_value = "mock_token"
    mock_get_users_for_role.side_effect = BusinessException(Error.DATA_NOT_FOUND, None)

    with pytest.raises(BusinessException) as exc_info:
        KEYCLOAK_SERVICE.get_user_emails_with_role("nonexistent_role")

    assert exc_info.value.code == Error.DATA_NOT_FOUND.name
    mock_get_users_for_role.assert_called_once_with("nonexistent_role")


@pytest.mark.asyncio
@patch("auth_api.services.keycloak.asyncio.sleep")
async def test_request_with_retry_returns_none_on_204(mock_sleep, session):
    """Test _request_with_retry returns None for 204 status code."""
    kg = KeycloakGroupSubscription(
        user_guid="test-user-id",
        product_code="test",
        group_name="test-group",
        group_action=KeycloakGroupActions.ADD_TO_GROUP.value,
    )

    mock_response = MagicMock()
    mock_response.status = 204
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session = AsyncMock()
    mock_session.request = AsyncMock(return_value=mock_response)

    result = await KeycloakService._request_with_retry(
        mock_session, "PUT", "http://test.com", {}, kg
    )

    assert result is None
    mock_session.request.assert_called_once()


@pytest.mark.asyncio
@patch("auth_api.services.keycloak.asyncio.sleep")
async def test_request_with_retry_retries_on_5xx_error(mock_sleep, session):
    """Test _request_with_retry retries on 5xx errors and succeeds."""
    kg = KeycloakGroupSubscription(
        user_guid="test-user-id",
        product_code="test",
        group_name="test-group",
        group_action=KeycloakGroupActions.ADD_TO_GROUP.value,
    )

    mock_response_success = MagicMock()
    mock_response_success.status = 204
    mock_response_success.__aenter__ = AsyncMock(return_value=mock_response_success)
    mock_response_success.__aexit__ = AsyncMock(return_value=None)

    mock_response_error = MagicMock()
    mock_response_error.status = 500
    mock_response_error.__aenter__ = AsyncMock(return_value=mock_response_error)
    mock_response_error.__aexit__ = AsyncMock(return_value=None)

    mock_session = AsyncMock()
    mock_session.request = AsyncMock(side_effect=[mock_response_error, mock_response_success])

    result = await KeycloakService._request_with_retry(
        mock_session, "PUT", "http://test.com", {}, kg
    )

    assert result is None
    assert mock_session.request.call_count == 2
    mock_sleep.assert_called_once()

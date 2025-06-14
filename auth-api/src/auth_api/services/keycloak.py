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
"""Utils for keycloak administration."""

import asyncio
import json
from string import Template
from typing import Dict, List

import aiohttp
import requests
from flask import current_app

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.dataclass import KeycloakGroupSubscription
from auth_api.utils.constants import (
    GROUP_ACCOUNT_HOLDERS,
    GROUP_ANONYMOUS_USERS,
    GROUP_GOV_ACCOUNT_USERS,
    GROUP_PUBLIC_USERS,
)
from auth_api.utils.enums import ContentType, KeycloakGroupActions, LoginSource
from auth_api.utils.roles import Role
from auth_api.utils.user_context import UserContext, user_context

from .keycloak_user import KeycloakUser


class KeycloakService:
    """For Keycloak services."""

    @staticmethod
    def add_user(user: KeycloakUser, return_if_exists: bool = False, throw_error_if_exists: bool = False):
        """Add user to Keycloak."""
        config = current_app.config
        # Add user and set password
        admin_token = KeycloakService._get_admin_token(upstream=True)

        base_url = config.get("KEYCLOAK_BCROS_BASE_URL")
        realm = config.get("KEYCLOAK_BCROS_REALMNAME")
        timeout = config.get("CONNECT_TIMEOUT", 60)

        # Check if the user exists
        if return_if_exists or throw_error_if_exists:
            existing_user = KeycloakService.get_user_by_username(user.user_name, admin_token=admin_token)
            if existing_user:
                if not throw_error_if_exists:
                    return existing_user
                raise BusinessException(Error.USER_ALREADY_EXISTS_IN_KEYCLOAK, None)
        # Add user to the keycloak group '$group_name'
        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}

        add_user_url = f"{base_url}/auth/admin/realms/{realm}/users"
        response = requests.post(add_user_url, data=user.value(), headers=headers, timeout=timeout)
        response.raise_for_status()

        return KeycloakService.get_user_by_username(user.user_name, admin_token)

    @staticmethod
    def update_user(user: KeycloakUser):
        """Add user to Keycloak."""
        config = current_app.config
        # Add user and set password
        admin_token = KeycloakService._get_admin_token(upstream=True)

        base_url = config.get("KEYCLOAK_BCROS_BASE_URL")
        realm = config.get("KEYCLOAK_BCROS_REALMNAME")
        timeout = current_app.config.get("CONNECT_TIMEOUT", 60)

        existing_user = KeycloakService.get_user_by_username(user.user_name, admin_token=admin_token)
        if not existing_user:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}

        update_user_url = f"{base_url}/auth/admin/realms/{realm}/users/{existing_user.id}"
        response = requests.put(update_user_url, data=user.value(), headers=headers, timeout=timeout)
        response.raise_for_status()

        return KeycloakService.get_user_by_username(user.user_name, admin_token)

    @staticmethod
    def get_user_by_username(username: str, admin_token=None) -> KeycloakUser:
        """Get user from Keycloak by username."""
        user = None
        base_url = current_app.config.get("KEYCLOAK_BCROS_BASE_URL")
        realm = current_app.config.get("KEYCLOAK_BCROS_REALMNAME")
        timeout = current_app.config.get("CONNECT_TIMEOUT", 60)
        if not admin_token:
            admin_token = KeycloakService._get_admin_token(upstream=True)

        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}

        # Get the user and return
        query_user_url = Template(f"{base_url}/auth/admin/realms/{realm}/users?username=$username").substitute(
            username=username
        )
        response = requests.get(query_user_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        if len(response.json()) == 1:
            user = KeycloakUser(response.json()[0])
        return user

    @staticmethod
    def get_user_groups(user_id, upstream: bool = False) -> KeycloakUser:
        """Get user from Keycloak by username."""
        base_url = (
            current_app.config.get("KEYCLOAK_BCROS_BASE_URL")
            if upstream
            else current_app.config.get("KEYCLOAK_BASE_URL")
        )
        realm = (
            current_app.config.get("KEYCLOAK_BCROS_REALMNAME")
            if upstream
            else current_app.config.get("KEYCLOAK_REALMNAME")
        )
        timeout = current_app.config.get("CONNECT_TIMEOUT", 60)
        admin_token = KeycloakService._get_admin_token(upstream=upstream)
        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}

        # Get the user and return
        query_user_url = f"{base_url}/auth/admin/realms/{realm}/users/{user_id}/groups"
        response = requests.get(query_user_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def delete_user_by_username(username):
        """Delete user from Keycloak by username."""
        admin_token = KeycloakService._get_admin_token(upstream=True)
        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}

        base_url = current_app.config.get("KEYCLOAK_BCROS_BASE_URL")
        realm = current_app.config.get("KEYCLOAK_BCROS_REALMNAME")
        timeout = current_app.config.get("CONNECT_TIMEOUT", 60)
        user = KeycloakService.get_user_by_username(username)

        if not user:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # Delete the user
        delete_user_url = f"{base_url}/auth/admin/realms/{realm}/users/{user.id}"
        response = requests.delete(delete_user_url, headers=headers, timeout=timeout)
        response.raise_for_status()

    @staticmethod
    def get_token(username, password):
        """Get user access token by username and password."""
        try:
            base_url = current_app.config.get("KEYCLOAK_BASE_URL")
            realm = current_app.config.get("KEYCLOAK_REALMNAME")
            token_request = (
                f"client_id={current_app.config.get('JWT_OIDC_AUDIENCE')}"
                f"&client_secret={current_app.config.get('JWT_OIDC_CLIENT_SECRET')}"
                f"&username={username}&password={password}&grant_type=password"
            )
            timeout = current_app.config.get("CONNECT_TIMEOUT", 60)

            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            token_url = f"{base_url}/auth/realms/{realm}/protocol/openid-connect/token"
            response = requests.post(token_url, data=token_request, headers=headers, timeout=timeout)

            response.raise_for_status()
            return response.json()
        except Exception as err:  # NOQA # pylint: disable=broad-except
            raise BusinessException(Error.INVALID_USER_CREDENTIALS, err) from err

    @staticmethod
    @user_context
    def join_users_group(**kwargs) -> str:
        """Add user to the group (public_users or anonymous_users) if the user is public."""
        user_from_context: UserContext = kwargs["user_context"]
        group_name: str = None
        login_source = user_from_context.login_source
        roles = user_from_context.roles

        # Cannot check the group from token, so check if the role 'edit' is already present.
        if login_source in (LoginSource.BCEID.value, LoginSource.BCSC.value) and Role.PUBLIC_USER.value not in roles:
            group_name = GROUP_PUBLIC_USERS
        elif (
            login_source == LoginSource.STAFF.value
            and Role.GOV_ACCOUNT_USER.value not in roles
            and Role.STAFF.value not in roles
        ):
            group_name = GROUP_GOV_ACCOUNT_USERS
        elif login_source == LoginSource.BCROS.value and Role.ANONYMOUS_USER.value not in roles:
            group_name = GROUP_ANONYMOUS_USERS

        if group_name:
            KeycloakService.add_user_to_group(user_from_context.sub, group_name)

        return group_name

    @staticmethod
    @user_context
    def join_account_holders_group(keycloak_guid: str = None, **kwargs):
        """Add user to the account holders group (account_holders) if the user is public."""
        # If keycloak_guid is provided add the user to the group directly, else find out from the token
        if not keycloak_guid:
            user_from_context: UserContext = kwargs["user_context"]
            # Cannot check the group from token, so check if the role 'account_holder' is already present.
            if Role.ACCOUNT_HOLDER.value in user_from_context.roles:
                return
            keycloak_guid = user_from_context.sub

        KeycloakService.add_user_to_group(keycloak_guid, GROUP_ACCOUNT_HOLDERS)

    @staticmethod
    @user_context
    def remove_from_account_holders_group(keycloak_guid: str = None, **kwargs):
        """Remove user from the group."""
        user_from_context: UserContext = kwargs["user_context"]
        if not keycloak_guid:
            keycloak_guid: Dict = user_from_context.sub

        if Role.ACCOUNT_HOLDER.value in user_from_context.roles:
            try:
                KeycloakService.remove_user_from_group(keycloak_guid, GROUP_ACCOUNT_HOLDERS)
            except Exception as err:
                current_app.logger.error(
                    f"Error removing user {user_from_context.sub} from account holders group: {err}"
                )

    @staticmethod
    @user_context
    def reset_otp(keycloak_guid: str = None, **kwargs):
        """Reset user one time  password from Keycloak."""
        if not keycloak_guid:
            user_from_context: UserContext = kwargs["user_context"]
            keycloak_guid: Dict = user_from_context.sub

        KeycloakService._reset_otp(keycloak_guid)

    @staticmethod
    def add_or_remove_product_keycloak_groups(kgs: List[KeycloakGroupSubscription]):
        """Call add_or_remove_users_from_group, by add to group then remove from group."""
        add_groups = [kg for kg in kgs if kg.group_action == KeycloakGroupActions.ADD_TO_GROUP.value]
        remove_groups = [kg for kg in kgs if kg.group_action == KeycloakGroupActions.REMOVE_FROM_GROUP.value]
        for keycloak_group_subscription in add_groups + remove_groups:
            current_app.logger.debug(
                f"Action: {keycloak_group_subscription.group_action} "
                f"Product: {keycloak_group_subscription.product_code} "
                f"Keycloak Group: {keycloak_group_subscription.group_name} "
                f"User guid: {keycloak_group_subscription.user_guid}"
            )
        asyncio.run(KeycloakService.add_or_remove_users_from_group(add_groups))
        asyncio.run(KeycloakService.add_or_remove_users_from_group(remove_groups))

    @staticmethod
    async def add_or_remove_users_from_group(kgs: List[KeycloakGroupSubscription]):
        """Asynchronously add/remove users from group - there can be upwards of 700+ users at once."""
        if not kgs:
            return
        config = current_app.config
        base_url, realm, timeout = (
            config.get("KEYCLOAK_BASE_URL"),
            config.get("KEYCLOAK_REALMNAME"),
            config.get("CONNECT_TIMEOUT", 60),
        )

        admin_token = KeycloakService._get_admin_token()
        group_names = {kg.group_name for kg in kgs}
        group_ids = {group_name: KeycloakService._get_group_id(admin_token, group_name) for group_name in group_names}
        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}

        method = "PUT" if kgs[0].group_action == KeycloakGroupActions.ADD_TO_GROUP.value else "DELETE"
        # Normal limit is 100, cap this to 40, so it doesn't hit keycloak too aggressively.
        connector = aiohttp.TCPConnector(limit=40)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [
                asyncio.create_task(
                    session.request(
                        method,
                        f"{base_url}/auth/admin/realms/{realm}/users/"
                        f"{kg.user_guid}/groups/{group_ids[kg.group_name]}",
                        headers=headers,
                        timeout=timeout,
                    )
                )
                for kg in kgs
            ]
            tasks = await asyncio.gather(*tasks, return_exceptions=True)
            for task in tasks:
                if isinstance(task, aiohttp.ClientConnectionError):
                    current_app.logger.error("Connection error")
                elif isinstance(task, asyncio.TimeoutError):
                    current_app.logger.error("Timeout error")
                elif isinstance(task, Exception):
                    current_app.logger.error(f"Exception: {task}")
                elif task.status != 204:
                    current_app.logger.error(f"Returned non 204: {task.method} - {task.url} - {task.status}")

    @staticmethod
    def get_user_emails_with_role(role: str):
        """Get user emails with the role name."""
        config = current_app.config
        base_url = config.get("KEYCLOAK_BASE_URL")
        realm = config.get("KEYCLOAK_REALMNAME")
        timeout = config.get("CONNECT_TIMEOUT", 60)
        admin_token = KeycloakService._get_admin_token()

        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}

        users = []
        get_role_users = f"{base_url}/auth/admin/realms/{realm}/roles/{role}/users"
        response = requests.get(get_role_users, headers=headers, timeout=timeout)
        if response.status_code == 404:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        response.raise_for_status()
        for user in response.json():
            users.append({"firstName": user["firstName"], "lastName": user["lastName"], "email": user["email"]})
        return users

    @staticmethod
    def add_user_to_group(user_id: str, group_name: str):
        """Add user to the keycloak group."""
        config = current_app.config
        base_url = config.get("KEYCLOAK_BASE_URL")
        realm = config.get("KEYCLOAK_REALMNAME")
        timeout = config.get("CONNECT_TIMEOUT", 60)
        # Create an admin token
        admin_token = KeycloakService._get_admin_token()
        # Get the '$group_name' group
        group_id = KeycloakService._get_group_id(admin_token, group_name)

        # Add user to the keycloak group '$group_name'
        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}
        add_to_group_url = f"{base_url}/auth/admin/realms/{realm}/users/{user_id}/groups/{group_id}"
        response = requests.put(add_to_group_url, headers=headers, timeout=timeout)
        response.raise_for_status()

    @staticmethod
    def remove_user_from_group(user_id: str, group_name: str):
        """Remove user from the keycloak group."""
        config = current_app.config
        base_url = config.get("KEYCLOAK_BASE_URL")
        realm = config.get("KEYCLOAK_REALMNAME")
        timeout = config.get("CONNECT_TIMEOUT", 60)
        # Create an admin token
        admin_token = KeycloakService._get_admin_token()
        # Get the '$group_name' group
        group_id = KeycloakService._get_group_id(admin_token, group_name)

        # Remove user from keycloak group '$group_name'
        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}
        remove_group_url = f"{base_url}/auth/admin/realms/{realm}/users/{user_id}/groups/{group_id}"
        response = requests.delete(remove_group_url, headers=headers, timeout=timeout)
        response.raise_for_status()

    @staticmethod
    def _get_admin_token(upstream: bool = False):
        """Create an admin token."""
        config = current_app.config
        base_url = config.get("KEYCLOAK_BCROS_BASE_URL") if upstream else config.get("KEYCLOAK_BASE_URL")
        realm = config.get("KEYCLOAK_BCROS_REALMNAME") if upstream else config.get("KEYCLOAK_REALMNAME")
        admin_client_id = (
            config.get("KEYCLOAK_BCROS_ADMIN_CLIENTID") if upstream else config.get("KEYCLOAK_ADMIN_USERNAME")
        )
        admin_secret = config.get("KEYCLOAK_BCROS_ADMIN_SECRET") if upstream else config.get("KEYCLOAK_ADMIN_SECRET")
        timeout = config.get("CONNECT_TIMEOUT", 60)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_url = f"{base_url}/auth/realms/{realm}/protocol/openid-connect/token"

        response = requests.post(
            token_url,
            data=f"client_id={admin_client_id}&grant_type=client_credentials" f"&client_secret={admin_secret}",
            headers=headers,
            timeout=timeout,
        )
        return response.json().get("access_token")

    @staticmethod
    def _get_group_id(admin_token: str, group_name: str):
        """Get a group id for the group name."""
        config = current_app.config
        base_url = config.get("KEYCLOAK_BASE_URL")
        realm = config.get("KEYCLOAK_REALMNAME")
        timeout = config.get("CONNECT_TIMEOUT", 60)
        get_group_url = f"{base_url}/auth/admin/realms/{realm}/groups?search={group_name}"
        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}
        response = requests.get(get_group_url, headers=headers, timeout=timeout)
        return KeycloakService._find_group_or_subgroup_id(response.json(), group_name)

    @staticmethod
    def _find_group_or_subgroup_id(groups: list, group_name: str):
        """Return group id by searching main and sub groups."""
        for group in groups:
            if group["name"] == group_name:
                return group["id"]
            if group_id := KeycloakService._find_group_or_subgroup_id(group["subGroups"], group_name):
                return group_id
        return None

    @staticmethod
    def _reset_otp(user_id: str):
        """Reset user one time  password from Keycloak."""
        config = current_app.config
        base_url = config.get("KEYCLOAK_BASE_URL")
        realm = config.get("KEYCLOAK_REALMNAME")
        timeout = config.get("CONNECT_TIMEOUT", 60)
        # Create an admin token
        admin_token = KeycloakService._get_admin_token()

        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}
        # step 1: add required action as configure otp
        configure_otp_url = f"{base_url}/auth/admin/realms/{realm}/users/{user_id}"
        input_data = json.dumps({"id": user_id, "requiredActions": ["CONFIGURE_TOTP"]})

        response = requests.put(configure_otp_url, headers=headers, data=input_data, timeout=timeout)

        if response.status_code == 204:
            get_credentials_url = f"{base_url}/auth/admin/realms/{realm}/users/{user_id}/credentials"
            response = requests.get(get_credentials_url, headers=headers, timeout=timeout)
            for credential in response.json():
                if credential["type"] == "otp":
                    delete_credential_url = f'{get_credentials_url}/{credential["id"]}'
                    response = requests.delete(delete_credential_url, headers=headers, timeout=timeout)
        response.raise_for_status()

    @staticmethod
    def create_client(client_representation: Dict[str, any]):
        """Create a client in keycloak."""
        config = current_app.config
        base_url = config.get("KEYCLOAK_BASE_URL")
        realm = config.get("KEYCLOAK_REALMNAME")
        timeout = config.get("CONNECT_TIMEOUT", 60)
        admin_token = KeycloakService._get_admin_token()

        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}

        create_client_url = f"{base_url}/auth/admin/realms/{realm}/clients"
        response = requests.post(
            create_client_url, data=json.dumps(client_representation), headers=headers, timeout=timeout
        )
        response.raise_for_status()

    @staticmethod
    def get_service_account_by_client_name(client_name: str):
        """Get client by name."""
        config = current_app.config
        base_url = config.get("KEYCLOAK_BASE_URL")
        realm = config.get("KEYCLOAK_REALMNAME")
        timeout = config.get("CONNECT_TIMEOUT", 60)
        admin_token = KeycloakService._get_admin_token()
        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{base_url}/auth/admin/realms/{realm}/clients?clientId={client_name}",
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        if len(response.json()) == 0:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        client_id = response.json()[0]["id"]
        return KeycloakService.get_service_account_user(client_id)

    @staticmethod
    def get_service_account_user(client_identifier: str):
        """Return service account user."""
        config = current_app.config
        base_url = config.get("KEYCLOAK_BASE_URL")
        realm = config.get("KEYCLOAK_REALMNAME")
        timeout = config.get("CONNECT_TIMEOUT", 60)
        admin_token = KeycloakService._get_admin_token()
        headers = {"Content-Type": ContentType.JSON.value, "Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{base_url}/auth/admin/realms/{realm}/clients/{client_identifier}/service-account-user",
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()

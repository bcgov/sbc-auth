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

import json
from typing import Dict

import requests
from flask import current_app, g

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.utils.constants import GROUP_ACCOUNT_HOLDERS, GROUP_ANONYMOUS_USERS, GROUP_PUBLIC_USERS
from auth_api.utils.enums import ContentType, LoginSource
from auth_api.utils.roles import Role

from .keycloak_user import KeycloakUser


class KeycloakService:
    """For Keycloak services."""

    @staticmethod
    def add_user(user: KeycloakUser, return_if_exists: bool = False, throw_error_if_exists: bool = False):
        """Add user to Keycloak."""
        config = current_app.config
        # Add user and set password
        admin_token = KeycloakService._get_admin_token(upstream=True)

        base_url = config.get('KEYCLOAK_BCROS_BASE_URL')
        realm = config.get('KEYCLOAK_BCROS_REALMNAME')

        # Check if the user exists
        if return_if_exists or throw_error_if_exists:
            existing_user = KeycloakService.get_user_by_username(user.user_name, admin_token=admin_token)
            if existing_user:
                if not throw_error_if_exists:
                    return existing_user
                raise BusinessException(Error.USER_ALREADY_EXISTS_IN_KEYCLOAK, None)
        # Add user to the keycloak group '$group_name'
        headers = {
            'Content-Type': ContentType.JSON.value,
            'Authorization': f'Bearer {admin_token}'
        }

        add_user_url = f'{base_url}/auth/admin/realms/{realm}/users'
        response = requests.post(add_user_url, data=user.value(), headers=headers)
        response.raise_for_status()

        return KeycloakService.get_user_by_username(user.user_name, admin_token)

    @staticmethod
    def update_user(user: KeycloakUser):
        """Add user to Keycloak."""
        config = current_app.config
        # Add user and set password
        admin_token = KeycloakService._get_admin_token(upstream=True)

        base_url = config.get('KEYCLOAK_BCROS_BASE_URL')
        realm = config.get('KEYCLOAK_BCROS_REALMNAME')

        existing_user = KeycloakService.get_user_by_username(user.user_name, admin_token=admin_token)
        if not existing_user:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        headers = {
            'Content-Type': ContentType.JSON.value,
            'Authorization': f'Bearer {admin_token}'
        }

        update_user_url = f'{base_url}/auth/admin/realms/{realm}/users/{existing_user.id}'
        response = requests.put(update_user_url, data=user.value(), headers=headers)
        response.raise_for_status()

        return KeycloakService.get_user_by_username(user.user_name, admin_token)

    @staticmethod
    def get_user_by_username(username, admin_token=None) -> KeycloakUser:
        """Get user from Keycloak by username."""
        user = None
        base_url = current_app.config.get('KEYCLOAK_BCROS_BASE_URL')
        realm = current_app.config.get('KEYCLOAK_BCROS_REALMNAME')
        if not admin_token:
            admin_token = KeycloakService._get_admin_token(upstream=True)

        headers = {
            'Content-Type': ContentType.JSON.value,
            'Authorization': f'Bearer {admin_token}'
        }

        # Get the user and return
        query_user_url = f'{base_url}/auth/admin/realms/{realm}/users?username={username}'
        response = requests.get(query_user_url, headers=headers)
        response.raise_for_status()
        if len(response.json()) == 1:
            user = KeycloakUser(response.json()[0])
        return user

    @staticmethod
    def get_user_groups(user_id, upstream: bool = False) -> KeycloakUser:
        """Get user from Keycloak by username."""
        base_url = current_app.config.get('KEYCLOAK_BCROS_BASE_URL') if upstream else current_app.config.get(
            'KEYCLOAK_BASE_URL')
        realm = current_app.config.get('KEYCLOAK_BCROS_REALMNAME') if upstream else current_app.config.get(
            'KEYCLOAK_REALMNAME')
        admin_token = KeycloakService._get_admin_token(upstream=upstream)
        headers = {
            'Content-Type': ContentType.JSON.value,
            'Authorization': f'Bearer {admin_token}'
        }

        # Get the user and return
        query_user_url = f'{base_url}/auth/admin/realms/{realm}/users/{user_id}/groups'
        response = requests.get(query_user_url, headers=headers)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def delete_user_by_username(username):
        """Delete user from Keycloak by username."""
        admin_token = KeycloakService._get_admin_token(upstream=True)
        headers = {
            'Content-Type': ContentType.JSON.value,
            'Authorization': f'Bearer {admin_token}'
        }

        base_url = current_app.config.get('KEYCLOAK_BCROS_BASE_URL')
        realm = current_app.config.get('KEYCLOAK_BCROS_REALMNAME')
        user = KeycloakService.get_user_by_username(username)

        if not user:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # Delete the user
        delete_user_url = f'{base_url}/auth/admin/realms/{realm}/users/{user.id}'
        response = requests.delete(delete_user_url, headers=headers)
        response.raise_for_status()

    @staticmethod
    def get_token(username, password):
        """Get user access token by username and password."""
        try:
            base_url = current_app.config.get('KEYCLOAK_BASE_URL')
            realm = current_app.config.get('KEYCLOAK_REALMNAME')
            token_request = 'client_id={}&client_secret={}&username={}&password={}&grant_type=password'.format(
                current_app.config.get('JWT_OIDC_AUDIENCE'),
                current_app.config.get('JWT_OIDC_CLIENT_SECRET'),
                username,
                password)

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            token_url = f'{base_url}/auth/realms/{realm}/protocol/openid-connect/token'
            response = requests.post(token_url, data=token_request, headers=headers)

            response.raise_for_status()
            return response.json()
        except Exception as err:
            raise BusinessException(Error.INVALID_USER_CREDENTIALS, err)

    @staticmethod
    def join_users_group(token_info: Dict):
        """Add user to the group (public_users or anonymous_users) if the user is public."""
        login_source = token_info.get('loginSource', None)

        # Cannot check the group from token, so check if the role 'edit' is already present.
        has_role = Role.EDITOR.value in token_info.get('realm_access').get('roles')

        if not has_role and login_source in (LoginSource.BCEID.value, LoginSource.BCSC.value, LoginSource.BCROS.value):
            group_name = GROUP_PUBLIC_USERS if login_source in (
                LoginSource.BCSC.value, LoginSource.BCEID.value) else GROUP_ANONYMOUS_USERS
            KeycloakService._add_user_to_group(token_info.get('sub'), group_name)

    @staticmethod
    def join_account_holders_group(keycloak_guid: str = None):
        """Add user to the account holders group (account_holders) if the user is public."""
        # If keycloak_guid is provided add the user to the group directly, else find out from the token
        if not keycloak_guid:
            token_info: Dict = KeycloakService._get_token_info()
            # Cannot check the group from token, so check if the role 'account_holder' is already present.
            if Role.ACCOUNT_HOLDER.value in token_info.get('realm_access').get('roles'):
                return
            keycloak_guid = token_info.get('sub')

        KeycloakService._add_user_to_group(keycloak_guid, GROUP_ACCOUNT_HOLDERS)

    @staticmethod
    def remove_from_account_holders_group(keycloak_guid: str = None):
        """Remove user from the group."""
        if not keycloak_guid:
            keycloak_guid: Dict = KeycloakService._get_token_info().get('sub')

        KeycloakService._remove_user_from_group(keycloak_guid, GROUP_ACCOUNT_HOLDERS)

    @staticmethod
    def reset_otp(keycloak_guid: str = None):
        """Reset user one time  password from Keycloak."""
        if not keycloak_guid:
            keycloak_guid: Dict = KeycloakService._get_token_info().get('sub')

        KeycloakService._reset_otp(keycloak_guid)

    @staticmethod
    def _add_user_to_group(user_id: str, group_name: str):
        """Add user to the keycloak group."""
        config = current_app.config
        base_url = config.get('KEYCLOAK_BASE_URL')
        realm = config.get('KEYCLOAK_REALMNAME')
        # Create an admin token
        admin_token = KeycloakService._get_admin_token()
        # Get the '$group_name' group
        group_id = KeycloakService._get_group_id(admin_token, group_name)

        # Add user to the keycloak group '$group_name'
        headers = {
            'Content-Type': ContentType.JSON.value,
            'Authorization': f'Bearer {admin_token}'
        }
        add_to_group_url = f'{base_url}/auth/admin/realms/{realm}/users/{user_id}/groups/{group_id}'
        response = requests.put(add_to_group_url, headers=headers)
        response.raise_for_status()

    @staticmethod
    def _remove_user_from_group(user_id: str, group_name: str):
        """Remove user from the keycloak group."""
        config = current_app.config
        base_url = config.get('KEYCLOAK_BASE_URL')
        realm = config.get('KEYCLOAK_REALMNAME')
        # Create an admin token
        admin_token = KeycloakService._get_admin_token()
        # Get the '$group_name' group
        group_id = KeycloakService._get_group_id(admin_token, group_name)

        # Add user to the keycloak group '$group_name'
        headers = {
            'Content-Type': ContentType.JSON.value,
            'Authorization': f'Bearer {admin_token}'
        }
        remove_group_url = f'{base_url}/auth/admin/realms/{realm}/users/{user_id}/groups/{group_id}'
        response = requests.delete(remove_group_url, headers=headers)
        response.raise_for_status()

    @staticmethod
    def _get_admin_token(upstream: bool = False):
        """Create an admin token."""
        config = current_app.config
        base_url = config.get('KEYCLOAK_BCROS_BASE_URL') if upstream else config.get('KEYCLOAK_BASE_URL')
        realm = config.get('KEYCLOAK_BCROS_REALMNAME') if upstream else config.get('KEYCLOAK_REALMNAME')
        admin_client_id = config.get('KEYCLOAK_BCROS_ADMIN_CLIENTID') if upstream else config.get(
            'KEYCLOAK_ADMIN_USERNAME')
        admin_secret = config.get('KEYCLOAK_BCROS_ADMIN_SECRET') if upstream else config.get('KEYCLOAK_ADMIN_SECRET')
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        token_url = f'{base_url}/auth/realms/{realm}/protocol/openid-connect/token'

        response = requests.post(token_url, data='client_id={}&grant_type=client_credentials&client_secret={}'.format(
            admin_client_id, admin_secret), headers=headers)
        return response.json().get('access_token')

    @staticmethod
    def _get_group_id(admin_token: str, group_name: str):
        """Get a group id for the group name."""
        config = current_app.config
        base_url = config.get('KEYCLOAK_BASE_URL')
        realm = config.get('KEYCLOAK_REALMNAME')
        get_group_url = f'{base_url}/auth/admin/realms/{realm}/groups?search={group_name}'
        headers = {
            'Content-Type': ContentType.JSON.value,
            'Authorization': f'Bearer {admin_token}'
        }
        response = requests.get(get_group_url, headers=headers)
        return response.json()[0].get('id')

    @staticmethod
    def _get_token_info():
        return g.jwt_oidc_token_info

    @staticmethod
    def _reset_otp(user_id: str):
        """Reset user one time  password from Keycloak."""
        config = current_app.config
        base_url = config.get('KEYCLOAK_BASE_URL')
        realm = config.get('KEYCLOAK_REALMNAME')
        # Create an admin token
        admin_token = KeycloakService._get_admin_token()

        headers = {
            'Content-Type': ContentType.JSON.value,
            'Authorization': f'Bearer {admin_token}'
        }
        # step 1: add required action as configure otp
        configure_otp_url = f'{base_url}/auth/admin/realms/{realm}/users/{user_id}'
        input_data = json.dumps(
            {
                'id': user_id,
                'requiredActions': ['CONFIGURE_TOTP']
            }
        )

        response = requests.put(configure_otp_url, headers=headers, data=input_data)

        if response.status_code == 204:
            # step 2: disable otp credential for Keycloak version under 8
            disable_otp_url = f'{base_url}/auth/admin/realms/{realm}/users/{user_id}/disable-credential-types'
            input_data = json.dumps(['otp'])
            response = requests.put(disable_otp_url, headers=headers, data=input_data)
            # if keycloak version is above 8 it will throw 415 error
            if response.status_code == 415:
                # step 3: delete otp credential for keyclaok version above 8
                get_credentials_url = f'{base_url}/auth/admin/realms/{realm}/users/{user_id}/credentials'
                response = requests.get(get_credentials_url, headers=headers)
                for credential in response.json():
                    if credential['type'] == 'otp':
                        delete_credential_url = f'{get_credentials_url}/{credential["id"]}'
                        response = requests.delete(delete_credential_url, headers=headers)
        response.raise_for_status()

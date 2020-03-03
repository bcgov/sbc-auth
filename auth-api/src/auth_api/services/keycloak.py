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

from typing import Dict

import requests
from flask import g, current_app
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakGetError

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.utils.constants import BCSC, GROUP_ACCOUNT_HOLDERS, GROUP_PUBLIC_USERS, PASSCODE
from auth_api.utils.roles import Role
from auth_api.utils.util import Singleton


class KeycloakConfig(metaclass=Singleton):  # pylint: disable=too-few-public-methods
    """Singleton wrapper for Keycloak Config."""

    __keycloak_admin = None
    __keycloak_openid = None

    def get_keycloak_admin(self):
        """Retrieve singleton keycloak_admin."""
        return self.__keycloak_admin

    def get_keycloak_openid(self):
        """Retrieve singleton keycloak_openid."""
        return self.__keycloak_openid

    def __init__(self):
        """Private constructor."""
        config = current_app.config
        self.__keycloak_admin = KeycloakAdmin(server_url=config.get('KEYCLOAK_BASE_URL') + '/auth/',
                                              username=config.get('KEYCLOAK_ADMIN_USERNAME'),
                                              password=config.get('KEYCLOAK_ADMIN_SECRET'),
                                              realm_name=config.get('KEYCLOAK_REALMNAME'),
                                              client_id=config.get('KEYCLOAK_ADMIN_USERNAME'),
                                              client_secret_key=config.get('KEYCLOAK_ADMIN_SECRET'),
                                              verify=True)

        self.__keycloak_openid = KeycloakOpenID(server_url=config.get('KEYCLOAK_BASE_URL') + '/auth/',
                                                realm_name=config.get('KEYCLOAK_REALMNAME'),
                                                client_id=config.get('KEYCLOAK_AUTH_AUDIENCE'),
                                                client_secret_key=config.get('KEYCLOAK_AUTH_CLIENT_SECRET'),
                                                verify=True)


class KeycloakService:
    """For Keycloak services."""

    def __init__(self):
        """Create Constructor."""
        super()

    # Add user to Keycloak
    def add_user(self, user_request):
        """Add user to Keycloak."""
        # New user default to enabled.
        enabled = user_request.get('enabled')
        if enabled is None:
            enabled = True

        # Add user and set password
        try:
            KeycloakConfig().get_keycloak_admin().create_user(
                {
                    'email': user_request.get('email'),
                    'username': user_request.get('username'),
                    'enabled': enabled,
                    'firstName': user_request.get('firstname'),
                    'lastName': user_request.get('lastname'),
                    'credentials': [{'value': user_request.get('password'), 'type': 'password'}],
                    'groups': user_request.get('user_type'),
                    'attributes': {'corp_type': user_request.get('corp_type'), 'source': user_request.get('source')}
                })

            user_id = KeycloakConfig().get_keycloak_admin().get_user_id(user_request.get('username'))

            # Set user groups
            if user_request.get('user_type'):
                for user_type in user_request.get('user_type'):
                    group = KeycloakConfig().get_keycloak_admin().get_group_by_path(user_type, True)
                    if group:
                        KeycloakConfig().get_keycloak_admin().group_user_add(user_id, group['id'])

            user = self.get_user_by_username(user_request.get('username'))

            return user
        except KeycloakGetError as err:
            if err.response_code == 409:
                raise BusinessException(Error.DATA_CONFLICT, err)
        except Exception as err:
            raise BusinessException(Error.UNDEFINED_ERROR, err)

    @staticmethod
    def get_user_by_username(username):
        """Get user from Keycloak by username."""
        try:
            # Get user id
            user_id_keycloak = KeycloakConfig().get_keycloak_admin().get_user_id(username)
        except Exception as err:
            raise BusinessException(Error.UNDEFINED_ERROR, err)
        # Get User
        if user_id_keycloak is not None:
            try:
                user = KeycloakConfig().get_keycloak_admin().get_user(user_id_keycloak)
                return user
            except Exception as err:
                raise BusinessException(Error.UNDEFINED_ERROR, err)
        else:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

    @staticmethod
    def delete_user_by_username(username):
        """Delete user from Keycloak by username."""
        try:
            # Get user id
            user_id_keycloak = KeycloakConfig().get_keycloak_admin().get_user_id(username)
        except Exception as err:
            raise BusinessException(Error.UNDEFINED_ERROR, err)
        # Delete User
        if user_id_keycloak is not None:
            try:
                response = KeycloakConfig().get_keycloak_admin().delete_user(user_id_keycloak)
                return response
            except Exception as err:
                raise BusinessException(Error.UNDEFINED_ERROR, err)
        else:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

    @staticmethod
    def get_token(username, password):
        """Get user access token by username and password."""
        try:
            response = KeycloakConfig().get_keycloak_openid().token(username, password)
            return response
        except Exception as err:
            raise BusinessException(Error.INVALID_USER_CREDENTIALS, err)

    @staticmethod
    def refresh_token(refresh_token):
        """Refresh user token."""
        try:
            response = KeycloakConfig().get_keycloak_openid().refresh_token(refresh_token, ['refresh_token'])
            return response
        except Exception as err:
            raise BusinessException(Error.INVALID_REFRESH_TOKEN, err)

    @staticmethod
    def logout(refresh_token):
        """Logout user by refresh-token."""
        try:
            response = KeycloakConfig().get_keycloak_openid().logout(refresh_token)
            return response
        except Exception as err:
            raise BusinessException(Error.INVALID_REFRESH_TOKEN, err)

    @staticmethod
    def join_public_users_group(token_info: Dict):
        """Add user to the public group (public_users) if the user is public."""
        is_public_user = token_info.get('loginSource', None) in (BCSC, PASSCODE)

        # Cannot check the group from token, so check if the role 'edit' is already present.
        has_role = Role.EDITOR.value in token_info.get('realm_access').get('roles')

        if not has_role and is_public_user:
            KeycloakService._add_user_to_group(token_info.get('sub'), GROUP_PUBLIC_USERS)

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
            'Content-Type': 'application/json',
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
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {admin_token}'
        }
        remove_group_url = f'{base_url}/auth/admin/realms/{realm}/users/{user_id}/groups/{group_id}'
        response = requests.delete(remove_group_url, headers=headers)
        response.raise_for_status()

    @staticmethod
    def _get_admin_token():
        """Create an admin token."""
        config = current_app.config
        base_url = config.get('KEYCLOAK_BASE_URL')
        realm = config.get('KEYCLOAK_REALMNAME')
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        token_url = f'{base_url}/auth/realms/{realm}/protocol/openid-connect/token'
        response = requests.post(token_url, data='client_id={}&grant_type=client_credentials&client_secret={}'.format(
            config.get('KEYCLOAK_ADMIN_USERNAME'), config.get('KEYCLOAK_ADMIN_SECRET')), headers=headers)
        return response.json().get('access_token')

    @staticmethod
    def _get_group_id(admin_token: str, group_name: str):
        """Get a group id for the group name."""
        config = current_app.config
        base_url = config.get('KEYCLOAK_BASE_URL')
        realm = config.get('KEYCLOAK_REALMNAME')
        get_group_url = f'{base_url}/auth/admin/realms/{realm}/groups?search={group_name}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {admin_token}'
        }
        response = requests.get(get_group_url, headers=headers)
        return response.json()[0].get('id')

    @staticmethod
    def _get_token_info():
        return g.jwt_oidc_token_info

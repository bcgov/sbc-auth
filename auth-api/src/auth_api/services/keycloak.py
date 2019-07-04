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

import os

from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakGetError

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error


KEYCLOAK_ADMIN = KeycloakAdmin(server_url=os.getenv('KEYCLOAK_BASE_URL') + '/auth/',
                               username=os.getenv('KEYCLOAK_ADMIN_CLIENTID'),
                               password=os.getenv('KEYCLOAK_ADMIN_SECRET'),
                               realm_name=os.getenv('KEYCLOAK_REALMNAME'),
                               client_id=os.getenv('KEYCLOAK_ADMIN_CLIENTID'),
                               client_secret_key=os.getenv('KEYCLOAK_ADMIN_SECRET'),
                               verify=True)


# Configure client
KEYCLOAK_OPENID = KeycloakOpenID(server_url=os.getenv('KEYCLOAK_BASE_URL') + '/auth/',
                                 realm_name=os.getenv('KEYCLOAK_REALMNAME'),
                                 client_id=os.getenv('KEYCLOAK_AUTH_AUDIENCE'),
                                 client_secret_key=os.getenv('KEYCLOAK_AUTH_CLIENT_SECRET'),
                                 verify=True)


class KeycloakService:
    """For Keycloak services."""

    def __init__(self):
        """Constructor."""
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
            KEYCLOAK_ADMIN.create_user(
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

            user_id = KEYCLOAK_ADMIN.get_user_id(user_request.get('username'))

            # Set user groups
            if user_request.get('user_type'):
                for user_type in user_request.get('user_type'):
                    group = KEYCLOAK_ADMIN.get_group_by_path(user_type, True)
                    if group:
                        KEYCLOAK_ADMIN.group_user_add(user_id, group['id'])

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
            user_id_keycloak = KEYCLOAK_ADMIN.get_user_id(username)
        except Exception as err:
            raise BusinessException(Error.UNDEFINED_ERROR, err)
        # Get User
        if user_id_keycloak is not None:
            try:
                user = KEYCLOAK_ADMIN.get_user(user_id_keycloak)
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
            user_id_keycloak = KEYCLOAK_ADMIN.get_user_id(username)
        except Exception as err:
            raise BusinessException(Error.UNDEFINED_ERROR, err)
        # Delete User
        if user_id_keycloak is not None:
            try:
                response = KEYCLOAK_ADMIN.delete_user(user_id_keycloak)
                return response
            except Exception as err:
                raise BusinessException(Error.UNDEFINED_ERROR, err)
        else:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

    @staticmethod
    def get_token(username, password):
        """Get user access token by username and password."""
        try:
            response = KEYCLOAK_OPENID.token(username, password)
            return response
        except Exception as err:
            raise BusinessException(Error.INVALID_USER_CREDENTIALS, err)

    @staticmethod
    def refresh_token(refresh_token):
        """Refresh user token."""
        try:
            response = KEYCLOAK_OPENID.refresh_token(refresh_token, ['refresh_token'])
            return response
        except Exception as err:
            raise BusinessException(Error.INVALID_REFRESH_TOKEN, err)

    @staticmethod
    def logout(refresh_token):
        """Logout user by refresh-token."""
        try:
            response = KEYCLOAK_OPENID.logout(refresh_token)
            return response
        except Exception as err:
            raise BusinessException(Error.INVALID_REFRESH_TOKEN, err)

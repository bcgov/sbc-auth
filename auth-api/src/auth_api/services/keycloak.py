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
"""utils for keycloak administration"""

from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenID
import json
import os

keycloak_admin = KeycloakAdmin(server_url=os.getenv("KEYCLOAK_BASE_URL") + "/auth/",
                               username=os.getenv("KEYCLOAK_ADMIN_CLIENTID"),
                               password=os.getenv("KEYCLOAK_ADMIN_SECRET"),
                               realm_name=os.getenv("KEYCLOAK_REALMNAME"),
                               client_id=os.getenv("KEYCLOAK_ADMIN_CLIENTID"),
                               client_secret_key=os.getenv("KEYCLOAK_ADMIN_SECRET"),
                               verify=True)

# keycloak_admin = KeycloakAdmin(server_url="http://localhost:8080/auth/",
#                                username='localtest',
#                                password='27f45971-0bee-44da-b5d6-34452a97b0b4',
#                                client_id='localtest',
#                                client_secret_key='27f45971-0bee-44da-b5d6-34452a97b0b4',
#                                realm_name="registries",
#                                verify=True)

# Configure client
keycloak_openid = KeycloakOpenID(server_url=os.getenv("KEYCLOAK_BASE_URL") + "/auth/",
                                 realm_name=os.getenv("KEYCLOAK_REALMNAME"),
                                 client_id=os.getenv("JWT_OIDC_AUDIENCE"),
                                 client_secret_key=os.getenv("JWT_OIDC_CLIENT_SECRET"),
                                 verify=True)


class KeycloakService:
    def __init__(self):
        super()

    # Add user to Keycloak
    def add_user(self, user_request):
        # New user default to enabled.
        enabled = user_request.get("enabled")
        if enabled == None:
            enabled = True

        # Add user and set password
        try:
            response = keycloak_admin.create_user({"email": user_request.get("email"),
                           "username": user_request.get("username"),
                           "enabled": enabled,
                           "firstName": user_request.get("firstname"),
                           "lastName": user_request.get("lastname"),
                           "credentials": [{"value": user_request.get("password"), "type": "password"}],
                           "groups": user_request.get("user_type"),
                           "attributes": {"corp_type": user_request.get("corp_type"), "source": user_request.get("source")}})

            user_id = keycloak_admin.get_user_id(user_request.get("username"))
            if user_request.get("user_type"):
                for user_type in user_request.get("user_type"):
                    group = keycloak_admin.get_group_by_path(user_type, True)
                    if group:
                        keycloak_admin.group_user_add(user_id, group["id"])

            user = self.get_user_by_username(user_request.get("username"))

            return user
        except Exception as err:
            raise err

    # Get user from Keycloak by username
    def get_user_by_username(self, username):
        try:
            # Get user id
            user_id_keycloak = keycloak_admin.get_user_id(username)
            # Get User
            user = keycloak_admin.get_user(user_id_keycloak)
            return user
        except Exception as err:
            raise err

    # Delete user from Keycloak by username
    def delete_user_by_username(self, username):
        try:
            user_id_keycloak = keycloak_admin.get_user_id(username)
            # Get User
            response = keycloak_admin.delete_user(user_id_keycloak)
            return response
        except Exception as err:
            raise err

    # Get user access token by username and password
    def get_token(self, username, password):
        return keycloak_openid.token(username, password)


    # Refresh user token
    def refresh_token(self, refresh_token):
        return keycloak_openid.refresh_token(refresh_token, ["refresh_token"])

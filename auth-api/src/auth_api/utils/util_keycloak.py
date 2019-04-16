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
import json
import os

class KeycloakUser:
    def __init__(self, username, password, firstname, lastname, email, enabled, user_type, source, corp_type):
        self.username = username
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.enabled = enabled
        self.user_type = user_type
        self.source = source
        self.corp_type = corp_type


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


# Add user
def add_user(keycloakuser):
    # Add user and set password
    response = keycloak_admin.create_user({"email": keycloakuser.email,
                   "username": keycloakuser.username,
                   "enabled": keycloakuser.enabled,
                   "firstName": keycloakuser.firstname,
                   "lastName": keycloakuser.lastname,
                   "credentials": [{"value": keycloakuser.password,"type": "password"}],
                   #"group": [keycloakuser.user_type, ],
                   "attributes": {"corp_type": keycloakuser.corp_type, "source": keycloakuser.source}})
    return response


# Get user from username
def get_user_by_username(username):
    # Get user id
    user_id_keycloak = keycloak_admin.get_user_id(username)
    # Get User
    user = keycloak_admin.get_user(user_id_keycloak)
    return user


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
"""Object to hold keycloak user information."""

import json

from auth_api.utils.enums import RequiredAction


class KeycloakUser:  # pylint: disable=too-many-instance-attributes
    """Object to hold keycloak user information."""

    def __init__(self, user: dict = None):
        """Create user."""
        self._user = user or {}

    @property
    def user_name(self) -> str:
        """Return the user_name."""
        return self._user.get("username")

    @user_name.setter
    def user_name(self, value: str):
        """Set the user_name."""
        self._user["username"] = value
        # Default first name to user name
        if not self.first_name:
            self.first_name = value

    @property
    def email(self) -> str:
        """Return the email."""
        return self._user.get("email")

    @email.setter
    def email(self, value: str):
        """Set the email."""
        self._user["email"] = value

    @property
    def enabled(self):
        """Return the enabled."""
        return self._user["enabled"]

    @enabled.setter
    def enabled(self, value: bool):
        """Set the enabled."""
        self._user["enabled"] = value

    @property
    def first_name(self) -> str:
        """Return the firstName."""
        return self._user.get("firstName")

    @first_name.setter
    def first_name(self, value: str):
        """Set the firstName."""
        self._user["firstName"] = value

    @property
    def last_name(self) -> str:
        """Return the last_name."""
        return self._user.get("lastName")

    @last_name.setter
    def last_name(self, value: str):
        """Set the last_name."""
        self._user["lastName"] = value

    @property
    def id(self) -> str:
        """Return the id."""
        return self._user.get("id")

    @id.setter
    def id(self, value: str):
        """Set the id."""
        self._user["id"] = value

    @property
    def password(self) -> str:
        """Return the password."""
        return self._user.get("credentials")[0].get("value", None)

    @password.setter
    def password(self, value: str):
        """Set the password."""
        self._user["credentials"] = [{}]
        self._user["credentials"][0]["value"] = value
        self._user["credentials"][0]["type"] = "password"

    @property
    def attributes(self) -> str:
        """Return the attributes."""
        return self._user.get("attributes")

    @attributes.setter
    def attributes(self, value: dict = None):
        """Set the attributes."""
        self._user["attributes"] = {}
        if value:
            for key in value.keys():
                self._user["attributes"][key] = value[key]

    def update_password_on_login(self):
        """Set the required_actions."""
        if not self._user.get("requiredActions", None):
            self._user["requiredActions"] = []
        self._user["requiredActions"].append(RequiredAction.UPDATE_PASSWORD.value)

    def configure_totp_on_login(self):
        """Set the required_actions."""
        if not self._user["requiredActions"]:
            self._user["requiredActions"] = []
        self._user["requiredActions"].append(RequiredAction.CONFIGURE_TOTP.value)

    def value(self) -> dict:
        """Return dict value."""
        return json.dumps(self._user)

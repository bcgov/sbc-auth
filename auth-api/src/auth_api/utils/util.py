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

"""CORS pre-flight decorator.

A simple decorator to add the options method to a Request Class.
"""

import base64
import os
import re
import urllib

import humps
from flask import current_app, request


def camelback2snake(camel_dict: dict):
    """Convert the passed dictionary's keys from camelBack case to snake_case."""
    return humps.decamelize(camel_dict)


def snake2camelback(snake_dict: dict):
    """Convert the passed dictionary's keys from snake_case to camelBack case."""
    return humps.camelize(snake_dict)


class Singleton(type):
    """Singleton meta."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call for meta."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def digitify(payload: str) -> int:
    """Return the digits from the string."""
    return int(re.sub(r"\D", "", payload))


def escape_wam_friendly_url(param):
    """Return encoded/escaped url."""
    base64_org_name = base64.b64encode(bytes(param, encoding="utf-8")).decode("utf-8")
    encode_org_name = urllib.parse.quote(base64_org_name, safe="")
    return encode_org_name


def mask_email(email: str) -> str:
    """Return masked email."""
    if email:
        parts = email.split("@")
        if len(parts) == 2:
            username, domain = parts
            masked_username = username[:2] + "*" * (len(username) - 2)
            masked_domain = domain[:2] + "*" * (len(domain) - 2)
            email = masked_username + "@" + masked_domain
    return email


def get_request_environment():
    """Return the environment corresponding to the user request."""
    env_override = request.headers.get('Environment-Override')
    sandbox_host = current_app.config.get("AUTH_WEB_SANDBOX_HOST")
    is_production = os.getenv("FLASK_ENV") == "production"
    
    if env_override:
        return env_override
    if is_production and sandbox_host in request.host_url:
        return "sandbox"
    return None


def extract_numbers(input_string: str):
    """Extract numbers from an input string."""
    if input_string is None:
        return None
    return "".join([char for char in input_string if char.isdigit()])

# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Registries Authentication Service.

This module is a wrapper for the Flask JwtManager
"""


class JWTWrapper:  # pylint: disable=too-few-public-methods
    """Singleton wrapper for Flask JwtManager."""

    from flask_jwt_oidc import JwtManager
    __instance = None

    @staticmethod
    def get_instance():
        """Retrieve singleton JwtManager."""
        if JWTWrapper.__instance is None:
            JWTWrapper()
        return JWTWrapper.__instance

    def __init__(self):
        """Virtually private constructor."""
        if JWTWrapper.__instance is not None:
            raise Exception('Attempt made to create multiple JWTWrappers')

        JWTWrapper.__instance = JWTWrapper.JwtManager()

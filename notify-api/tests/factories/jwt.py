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

"""JWT factory."""
import os
from enum import Enum
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


class JwtFactory(dict, Enum):
    """Jwt factory."""

    JWT_HEADER = {
        'kid': 'sbc-auth-web',
        'kty': 'RSA',
        'alg': 'RS256'
    }

    @staticmethod
    def factory_auth_header(jwt, claims):
        """Produce JWT tokens for use in tests."""
        return {'Authorization': 'Bearer ' + jwt.create_testing_jwt(claims=claims, header=JwtFactory.JWT_HEADER.value)}

    @staticmethod
    def get_private_key():
        """Get private key."""
        current_dir = Path(__file__)
        with open(os.path.join(current_dir.parent, './keys/test-key.pem'), 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        return private_key

    @staticmethod
    def get_public_key():
        """Get public key."""
        current_dir = Path(__file__)
        with open(os.path.join(current_dir.parent, './keys/test-key.pub'), 'rb') as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        return public_key


class JwtClaimsFactory(dict, Enum):
    """Test scenarios of jwt claims."""

    public_user_role = {
        'iss': 'test',
        'sub': 'test',
        'firstname': 'Test',
        'lastname': 'User',
        'username': 'testuser',
        'realm_access': {
            'roles': [
                'public_user'
            ]
        }
    }

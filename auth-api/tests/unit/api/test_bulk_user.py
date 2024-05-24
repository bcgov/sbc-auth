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

"""Tests to assure the users API end-point.

Test-Suite to ensure that the /users endpoint is working as expected.
"""
import json
import uuid
from random import randint


from auth_api import status as http_status
from auth_api.config import get_named_config
from auth_api.schemas import utils as schema_utils
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.enums import IdpHint, ProductCode
from tests.utilities.factory_scenarios import BulkUserTestScenario, TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_auth_header, factory_invitation_anonymous


KEYCLOAK_SERVICE = KeycloakService()

CONFIG = get_named_config('testing')


def test_add_user(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv.json, 'user_response')[0]


def test_add_user_admin_valid_bcros(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org admin can create members."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_dir_search_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_anonymous),
                     headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation_anonymous(org_id=org_id)),
                     headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    assert dictionary.get('token') is not None
    assert rv.status_code == http_status.HTTP_201_CREATED

    user = {
        'username': 'testuser{}'.format(randint(0, 1000)),
        'password': 'Password@1234',
    }
    rv = client.post('/api/v1/users/bcros', data=json.dumps(user),
                     headers={'invitation_token': dictionary.get('token')}, content_type='application/json')

    # Login as this user
    invited_user_token = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': str(uuid.uuid4()),
        'firstname': 'Test',
        'lastname': 'User',
        'preferred_username': 'bcros/{}'.format(user.get('username')),
        'realm_access': {
            'roles': []
        },
        'roles': [],
        'accessType': 'ANONYMOUS',
        'product_code': ProductCode.DIR_SEARCH.value
    }
    headers = factory_auth_header(jwt=jwt, claims=invited_user_token)

    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # headers = factory_auth_header(jwt=jwt,
    #                               claims=TestJwtClaims.anonymous_bcros_role)
    user_input = BulkUserTestScenario.get_bulk_user1_for_org(org_id)
    rv = client.post('/api/v1/bulk/users', headers=headers,
                     data=json.dumps(user_input),
                     content_type='application/json')
    assert len(rv.json['users']) == 2
    assert schema_utils.validate(rv.json, 'anonymous_user_response')[0]

    assert rv.json['users'][0]['httpStatus'] == 201
    assert rv.json['users'][0]['httpStatus'] == 201
    assert rv.json['users'][0]['error'] == ''
    assert rv.json['users'][1]['error'] == ''
    assert rv.json['users'][0]['username'] == IdpHint.BCROS.value + '/' + user_input['users'][0]['username']
    assert rv.json['users'][1]['username'] == IdpHint.BCROS.value + '/' + user_input['users'][1]['username']

    rv = client.post('/api/v1/bulk/users', headers=headers,
                     data=json.dumps(user_input),
                     content_type='application/json')

    assert len(rv.json['users']) == 2
    assert schema_utils.validate(rv.json, 'anonymous_user_response')[0]
    assert rv.json['users'][0]['httpStatus'] == 409
    assert rv.json['users'][1]['httpStatus'] == 409
    assert rv.json['users'][0]['error'] == 'The username is already taken'
    assert rv.json['users'][1]['error'] == 'The username is already taken'

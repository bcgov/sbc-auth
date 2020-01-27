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

"""Tests to verify the entities API end-point.

Test-Suite to ensure that the /entities endpoint is working as expected.
"""

import copy
import json
from unittest.mock import patch

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.services import Entity as EntityService
from tests.utilities.factory_scenarios import TestContactInfo, TestEntityInfo, TestJwtClaims
from tests.utilities.factory_utils import (
    factory_affiliation_model, factory_auth_header, factory_entity_model, factory_membership_model, factory_org_model,
    factory_user_model)


def test_add_entity(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an entity can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_add_entity_invalid_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid entity returns a 400."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.system_role)
    rv = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.invalid),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_entity_no_auth_returns_401(client, session):  # pylint:disable=unused-argument
    """Assert that POSTing an entity without an auth header returns a 401."""
    rv = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                     headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_add_entity_invalid_returns_exception(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid entity returns an exception."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.system_role)
    with patch.object(EntityService, 'save_entity', side_effect=BusinessException(Error.DATA_ALREADY_EXISTS, None)):
        rv = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                         headers=headers, content_type='application/json')
        assert rv.status_code == 400


def test_get_entity(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an entity can be retrieved via GET."""
    headers_system = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv_create = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                            headers=headers_system, content_type='application/json')
    assert rv_create.status_code == http_status.HTTP_201_CREATED

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)

    rv = client.get('/api/v1/entities/{}'.format(TestEntityInfo.entity1['businessIdentifier']),
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['businessIdentifier'] == TestEntityInfo.entity1['businessIdentifier']


def test_get_entity_unauthorized_user_returns_403(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an entity can be retrieved via GET."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                headers=headers, content_type='application/json')

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)

    rv = client.get('/api/v1/entities/{}'.format(TestEntityInfo.entity1['businessIdentifier']),
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_403_FORBIDDEN


def test_get_entity_no_auth_returns_401(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an entity cannot be retrieved without an authorization header."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                headers=headers, content_type='application/json')
    rv = client.get('/api/v1/entities/{}'.format(TestEntityInfo.entity1['businessIdentifier']),
                    headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_get_entity_no_entity_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that attempting to retrieve a non-existent entity returns a 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.get('/api/v1/entities/{}'.format(TestEntityInfo.entity1['businessIdentifier']),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_add_contact(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an entity."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    rv = client.post('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                     headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TestContactInfo.contact1['email']


def test_add_contact_invalid_format_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding an invalidly formatted contact returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                headers=headers, content_type='application/json')
    rv = client.post('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                     headers=headers, data=json.dumps(TestContactInfo.invalid), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_contact_no_entity_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact to a non-existant Entity returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                     headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_add_contact_duplicate_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a duplicate contact to an Entity returns 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                headers=headers, content_type='application/json')
    client.post('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    rv = client.post('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                     headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a contact can be updated on an entity."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                headers=headers, content_type='application/json')
    rv = client.post('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                     headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    rv = client.put('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                    headers=headers, data=json.dumps(TestContactInfo.contact2), content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert len(dictionary['contacts']) == 1
    assert dictionary['contacts'][0]['email'] == TestContactInfo.contact2['email']


def test_update_contact_invalid_format_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating with an invalidly formatted contact returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role)
    client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                headers=headers, content_type='application/json')
    client.post('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    rv = client.put('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                    headers=headers, data=json.dumps(TestContactInfo.invalid), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact_no_entity_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating a contact on a non-existant entity returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.put('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                    headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_update_contact_missing_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating a non-existant contact returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                headers=headers, content_type='application/json')
    rv = client.put('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                    headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_authorizations_passcode_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for passcode user returns 200."""
    inc_number = 'CP1234567'

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.get(f'/api/v1/entities/{inc_number}/authorizations',
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('orgMembership') == 'OWNER'

    # Test with invalid number
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.get('/api/v1/entities/INVALID/authorizations',
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('role', None) is None


def test_update_entity_success(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an entity can be updated."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    client.post('/api/v1/entities/{}/contacts'.format(TestEntityInfo.entity1['businessIdentifier']),
                headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')

    rv = client.put('/api/v1/entities/{}'.format(TestEntityInfo.entity1['businessIdentifier']),
                    data=json.dumps(TestEntityInfo.entity2),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['businessIdentifier'] == TestEntityInfo.entity2['businessIdentifier']

    # test business id alone can be updated
    rv = client.put('/api/v1/entities/{}'.format(TestEntityInfo.entity2['businessIdentifier']),
                    data=json.dumps({'businessIdentifier': 'CPNEW123'}),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['businessIdentifier'] == 'CPNEW123'


def test_update_entity_failures(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that an entity can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)

    rv = client.put('/api/v1/entities/{}'.format('1234'),
                    data=json.dumps(TestEntityInfo.entity2),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND

    rv = client.put('/api/v1/entities/{}'.format('1234'),
                    data=json.dumps(TestEntityInfo.entity2),
                    content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_authorizations_for_staff_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for staff user returns 200."""
    inc_number = 'tester'

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get(f'/api/v1/entities/{inc_number}/authorizations',
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK


def test_authorizations_for_affiliated_users_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for affiliated users returns 200."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    claims = copy.deepcopy(TestJwtClaims.passcode.value)
    claims['sub'] = str(user.keycloak_guid)

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f'/api/v1/entities/{entity.business_identifier}/authorizations',
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('orgMembership') == 'OWNER'

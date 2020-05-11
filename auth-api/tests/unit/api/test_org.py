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

"""Tests to verify the orgs API end-point.

Test-Suite to ensure that the /orgs endpoint is working as expected.
"""

import json
from unittest.mock import patch

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import Invitation as InvitationService
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService
from auth_api.utils.enums import OrgType
from tests.utilities.factory_scenarios import (
    TestAffliationInfo, TestContactInfo, TestEntityInfo, TestJwtClaims, TestOrgInfo)
from tests.utilities.factory_utils import factory_auth_header, factory_invitation


def test_add_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_add_anonymous_org_staff_admin(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_anonymous),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    assert dictionary['accessType'] == 'ANONYMOUS'


def test_add_anonymous_org_by_user_exception(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_anonymous),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_add_org_staff_admin_anonymous_not_passed(client, jwt, session,
                                                  keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps({'name': 'My Test Org'}),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    assert dictionary['accessType'] == 'ANONYMOUS'


def test_add_org_staff_admin_any_number_of_orgs(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org2),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org3),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org4),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org5),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_add_org_multiple(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed.But in limited number."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv1 = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                      headers=headers, content_type='application/json')
    assert rv1.status_code == http_status.HTTP_201_CREATED
    rv2 = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org2),
                      headers=headers, content_type='application/json')
    assert rv2.status_code == http_status.HTTP_201_CREATED
    rv3 = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org3),
                      headers=headers, content_type='application/json')
    assert rv3.status_code == http_status.HTTP_201_CREATED
    rv4 = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org4),
                      headers=headers, content_type='application/json')

    assert rv4.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_same_org_409(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_409_CONFLICT


def test_add_org_invalid_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 400."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.invalid),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_org_invalid_space_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 400."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.invalid_name_space),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_org_invalid_spaces_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 400."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.invalid_name_spaces),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_org_invalid_end_space_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 400."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.invalid_name_end_space),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_org_invalid_start_space_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 400."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.invalid_name_start_space),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_org_invalid_returns_401(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 401."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.view_role)
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_add_org_normal_staff_invalid_returns_401(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 401."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.staff_role)
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_add_org_invalid_user_returns_401(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an org with invalid user returns a 401."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)

    with patch.object(UserService, 'find_by_jwt_token', return_value=None):
        rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                         headers=headers, content_type='application/json')
        assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_add_org_invalid_returns_exception(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns an exception."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')

    with patch.object(OrgService, 'create_org', side_effect=BusinessException(Error.DATA_ALREADY_EXISTS, None)):
        rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                         headers=headers, content_type='application/json')
        assert rv.status_code == 400


def test_get_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be retrieved via GET."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.get('/api/v1/orgs/{}'.format(org_id),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['id'] == org_id


def test_get_org_no_auth_returns_401(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org cannot be retrieved without an authorization header."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.get('/api/v1/orgs/{}'.format(org_id),
                    headers=None, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_get_org_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that attempting to retrieve a non-existent org returns a 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get('/api/v1/orgs/{}'.format(999),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_update_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.put('/api/v1/orgs/{}'.format(org_id), data=json.dumps({'name': 'helo'}),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['id'] == org_id

    rv = client.post('/api/v1/orgs', data=json.dumps({'name': 'helo-duplicate'}),
                     headers=headers, content_type='application/json')

    rv = client.put('/api/v1/orgs/{}'.format(org_id), data=json.dumps({'name': 'helo-duplicate'}),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_409_CONFLICT


def test_upgrade_anon_org_fail(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_anonymous),
                     headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert rv.json.get('orgType') == OrgType.BASIC.value
    assert rv.json.get('name') == TestOrgInfo.org1.get('name')

    org_id = dictionary['id']
    # upgrade with same data

    premium_info = TestOrgInfo.bcol_linked()
    premium_info['typeCode'] = OrgType.PREMIUM.value

    rv = client.put('/api/v1/orgs/{}?action=UPGRADE'.format(org_id),
                    data=json.dumps(premium_info), headers=headers,
                    content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_upgrade_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert rv.json.get('orgType') == OrgType.BASIC.value
    assert rv.json.get('name') == TestOrgInfo.org1.get('name')

    org_id = dictionary['id']
    # upgrade with same data

    premium_info = TestOrgInfo.bcol_linked()
    premium_info['typeCode'] = OrgType.PREMIUM.value

    rv = client.put('/api/v1/orgs/{}?action=UPGRADE'.format(org_id),
                    data=json.dumps(premium_info), headers=headers,
                    content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK

    rv = client.get('/api/v1/orgs/{}'.format(org_id),
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['id'] == org_id
    assert rv.json.get('orgType') == OrgType.PREMIUM.value
    assert rv.json.get('name') == premium_info['name']


def test_upgrade_downgrade_reattach_bcol_todifferent_org(client, jwt, session,
                                                         keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    bcol_account = TestOrgInfo.bcol_linked()
    rv = client.post('/api/v1/orgs', data=json.dumps(bcol_account),
                     headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert rv.json.get('orgType') == OrgType.PREMIUM.value
    assert rv.json.get('name') == bcol_account.get('name')
    org_id = dictionary['id']

    # create a new org with same bcol
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    bcol_account = TestOrgInfo.bcol_linked()
    rv = client.post('/api/v1/orgs', data=json.dumps(bcol_account),
                     headers=headers, content_type='application/json')

    # should fail since BCOL is already attached
    assert rv.status_code == http_status.HTTP_409_CONFLICT

    # downgrade with same data
    rv = client.put('/api/v1/orgs/{}?action=DOWNGRADE'.format(org_id),
                    data=json.dumps({'name': 'My Test Orgs', 'typeCode': 'BASIC'}), headers=headers,
                    content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK

    rv = client.get('/api/v1/orgs/{}'.format(org_id),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['id'] == org_id
    assert rv.json.get('orgType') == OrgType.BASIC.value
    assert rv.json.get('name') == 'My Test Orgs'

    # create a new org with same bcol
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    bcol_account = TestOrgInfo.bcol_linked()
    rv = client.post('/api/v1/orgs', data=json.dumps(bcol_account),
                     headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert rv.json.get('orgType') == OrgType.PREMIUM.value
    assert rv.json.get('name') == bcol_account.get('name')


def test_downgrade_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    bcol_account = TestOrgInfo.bcol_linked()
    rv = client.post('/api/v1/orgs', data=json.dumps(bcol_account),
                     headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert rv.json.get('orgType') == OrgType.PREMIUM.value
    assert rv.json.get('name') == bcol_account.get('name')

    org_id = dictionary['id']
    # downgrade with same data
    rv = client.put('/api/v1/orgs/{}?action=DOWNGRADE'.format(org_id),
                    data=json.dumps({'name': 'My Test Orgs', 'typeCode': 'BASIC'}), headers=headers,
                    content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK

    rv = client.get('/api/v1/orgs/{}'.format(org_id),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['id'] == org_id
    assert rv.json.get('orgType') == OrgType.BASIC.value
    assert rv.json.get('name') == 'My Test Orgs'


def test_update_premium_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.bcol_linked()),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert rv.json.get('orgType') == OrgType.PREMIUM.value
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    # Update with same data
    rv = client.put('/api/v1/orgs/{}'.format(org_id), data=json.dumps(TestOrgInfo.bcol_linked()), headers=headers,
                    content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK


def test_get_org_payment_settings(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.bcol_linked()),
                     headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_201_CREATED
    assert rv.json.get('orgType') == OrgType.PREMIUM.value

    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.get('/api/v1/orgs/{}/contacts'.format(org_id), headers=headers)

    # Update with same data
    rv = client.get('/api/v1/orgs/{}/payment_settings'.format(org_id), headers=headers)
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)


def test_update_org_returns_400(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can not be updated and return 400 error via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.put('/api/v1/orgs/{}'.format(org_id), data=json.dumps(TestOrgInfo.invalid),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_org_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that attempting to update a non-existent org returns a 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.put('/api/v1/orgs/{}'.format(999), data=json.dumps(TestOrgInfo.org1),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_update_org_returns_exception(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that attempting to update a non-existent org returns an exception."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    with patch.object(OrgService, 'update_org', side_effect=BusinessException(Error.DATA_ALREADY_EXISTS, None)):
        rv = client.put('/api/v1/orgs/{}'.format(org_id), data=json.dumps(TestOrgInfo.org1),
                        headers=headers, content_type='application/json')
        assert rv.status_code == 400


def test_add_contact(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an org."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                     headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    assert dictionary['email'] == TestContactInfo.contact1['email']


def test_add_contact_invalid_format_returns_400(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that adding an invalidly formatted contact returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                     headers=headers, data=json.dumps(TestContactInfo.invalid), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_contact_valid_email_returns_201(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that adding an valid formatted contact with special characters in email returns a 201."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                     headers=headers, data=json.dumps(TestContactInfo.email_valid), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_add_contact_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact to a non-existant org returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/orgs/{}/contacts'.format(99),
                     headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_add_contact_duplicate_returns_400(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that adding a duplicate contact to an org returns 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    rv = client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                     headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a contact can be updated on an org."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                     headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    rv = client.put('/api/v1/orgs/{}/contacts'.format(org_id),
                    headers=headers, data=json.dumps(TestContactInfo.contact2), content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['email'] == TestContactInfo.contact2['email']


def test_update_contact_invalid_format_returns_400(client, jwt, session,
                                                   keycloak_mock):  # pylint:disable=unused-argument
    """Assert that updating with an invalidly formatted contact returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    rv = client.put('/api/v1/orgs/{}/contacts'.format(org_id),
                    headers=headers, data=json.dumps(TestContactInfo.invalid), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_update_contact_valid_email_format_returns_200(client, jwt, session,
                                                       keycloak_mock):  # pylint:disable=unused-argument
    """Assert that updating with an validly formatted contact with special characters in email returns a 200."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    rv = client.put('/api/v1/orgs/{}/contacts'.format(org_id),
                    headers=headers, data=json.dumps(TestContactInfo.email_valid), content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK


def test_update_contact_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating a contact on a non-existant entity returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.put('/api/v1/orgs/{}/contacts'.format(99),
                    headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_update_contact_missing_returns_404(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that updating a non-existant contact returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.put('/api/v1/orgs/{}/contacts'.format(org_id),
                    headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_delete_contact(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a contact can be deleted on an org."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/contacts'.format(org_id),
                     headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    rv = client.delete('/api/v1/orgs/{}/contacts'.format(org_id),
                       headers=headers, data=json.dumps(TestContactInfo.contact2), content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK

    rv = client.get('/api/v1/orgs/{}/contacts'.format(org_id), headers=headers)

    dictionary = None
    dictionary = json.loads(rv.data)

    assert len(dictionary['contacts']) == 0


def test_delete_contact_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that deleting a contact on a non-existant entity returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.delete('/api/v1/orgs/{}/contacts'.format(99),
                       headers=headers, data=json.dumps(TestContactInfo.contact1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_delete_contact_returns_exception(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that attempting to delete an org returns an exception."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    with patch.object(OrgService, 'delete_contact', side_effect=BusinessException(Error.DATA_ALREADY_EXISTS, None)):
        rv = client.delete('/api/v1/orgs/{}/contacts'.format(org_id), headers=headers, content_type='application/json')
        assert rv.status_code == 400


def test_get_members(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a list of members for an org can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.get('/api/v1/orgs/{}/members'.format(org_id),
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['members']
    assert len(dictionary['members']) == 1
    assert dictionary['members'][0]['membershipTypeCode'] == 'OWNER'


def test_delete_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be deleted."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.delete('/api/v1/orgs/{}'.format(org_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT


def test_delete_org_failure_affiliation(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org cannnot be deleted with valid affiliation."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity_lear_mock),
                     headers=headers, content_type='application/json')
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    rv = client.post('/api/v1/orgs/{}/affiliations'.format(org_id), headers=headers,
                     data=json.dumps(TestAffliationInfo.affiliation3), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    rv = client.delete('/api/v1/orgs/{}'.format(org_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_406_NOT_ACCEPTABLE


def test_delete_org_failure_members(client, jwt, session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a member of an org can have their role updated."""
    # Set up: create/login user, create org
    headers_invitee = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers_invitee, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers_invitee, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    # Invite a user to the org
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id, 'abc123@email.com')),
                     headers=headers_invitee, content_type='application/json')
    dictionary = json.loads(rv.data)
    invitation_id = dictionary['id']
    invitation_id_token = InvitationService.generate_confirmation_token(invitation_id)

    # Create/login as invited user
    headers_invited = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role_2)
    rv = client.post('/api/v1/users', headers=headers_invited, content_type='application/json')

    # Accept invite as invited user
    rv = client.put('/api/v1/invitations/tokens/{}'.format(invitation_id_token),
                    headers=headers_invited, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['status'] == 'ACCEPTED'

    # Get pending members for the org as invitee and assert length of 1
    rv = client.get('/api/v1/orgs/{}/members?status=PENDING_APPROVAL'.format(org_id), headers=headers_invitee)
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['members']
    assert len(dictionary['members']) == 1

    # Find the pending member
    new_member = dictionary['members'][0]
    assert new_member['membershipTypeCode'] == 'MEMBER'
    member_id = new_member['id']

    # Update the new member
    rv = client.patch('/api/v1/orgs/{}/members/{}'.format(org_id, member_id), headers=headers_invitee,
                      data=json.dumps({'role': 'ADMIN'}), content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['membershipTypeCode'] == 'ADMIN'

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.delete('/api/v1/orgs/{}'.format(org_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_406_NOT_ACCEPTABLE


def test_get_invitations(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a list of invitations for an org can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id, 'abc123@email.com')),
                     headers=headers, content_type='application/json')

    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id, 'xyz456@email.com')),
                     headers=headers, content_type='application/json')

    rv = client.get('/api/v1/orgs/{}/invitations'.format(org_id),
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['invitations']
    assert len(dictionary['invitations']) == 2
    assert dictionary['invitations'][0]['recipientEmail'] == 'abc123@email.com'
    assert dictionary['invitations'][1]['recipientEmail'] == 'xyz456@email.com'


def test_update_anon_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_anonymous),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    assert dictionary['accessType'] == 'ANONYMOUS'
    org_id = dictionary['id']
    rv = client.put('/api/v1/orgs/{}'.format(org_id), data=json.dumps({'name': 'helo2'}),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['name'] == 'helo2'

    public_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.put('/api/v1/orgs/{}'.format(org_id), data=json.dumps({'name': 'helo2'}),
                    headers=public_headers, content_type='application/json')
    # not an admin/owner..so unauthorized will be thrown when trying to access it
    assert rv.status_code == http_status.HTTP_403_FORBIDDEN


def test_update_member(client, jwt, session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a member of an org can have their role updated."""
    # Set up: create/login user, create org
    headers_invitee = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers_invitee, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers_invitee, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    # Invite a user to the org
    rv = client.post('/api/v1/invitations', data=json.dumps(factory_invitation(org_id, 'abc123@email.com')),
                     headers=headers_invitee, content_type='application/json')
    dictionary = json.loads(rv.data)
    invitation_id = dictionary['id']
    invitation_id_token = InvitationService.generate_confirmation_token(invitation_id)

    # Create/login as invited user
    headers_invited = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role_2)
    rv = client.post('/api/v1/users', headers=headers_invited, content_type='application/json')

    # Accept invite as invited user
    rv = client.put('/api/v1/invitations/tokens/{}'.format(invitation_id_token),
                    headers=headers_invited, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['status'] == 'ACCEPTED'

    # Get pending members for the org as invitee and assert length of 1
    rv = client.get('/api/v1/orgs/{}/members?status=PENDING_APPROVAL'.format(org_id), headers=headers_invitee)
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['members']
    assert len(dictionary['members']) == 1

    # Find the pending member
    new_member = dictionary['members'][0]
    assert new_member['membershipTypeCode'] == 'MEMBER'
    member_id = new_member['id']

    # Update the new member
    rv = client.patch('/api/v1/orgs/{}/members/{}'.format(org_id, member_id), headers=headers_invitee,
                      data=json.dumps({'role': 'ADMIN'}), content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['membershipTypeCode'] == 'ADMIN'


def test_add_affiliation(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an org."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity_lear_mock),
                     headers=headers, content_type='application/json')
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/affiliations'.format(org_id), headers=headers,
                     data=json.dumps(TestAffliationInfo.affiliation3), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    assert dictionary['organization']['id'] == org_id


def test_add_affiliation_invalid_format_returns_400(client, jwt, session,
                                                    keycloak_mock):  # pylint:disable=unused-argument
    """Assert that adding an invalidly formatted affiliations returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/affiliations'.format(org_id),
                     headers=headers, data=json.dumps(TestAffliationInfo.invalid), content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_affiliation_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact to a non-existant org returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/orgs/{}/affiliations'.format(99), headers=headers,
                     data=json.dumps(TestAffliationInfo.affliation1), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_add_affiliation_returns_exception(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that attempting to delete an affiliation returns an exception."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity1),
                     headers=headers, content_type='application/json')
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    with patch.object(AffiliationService, 'create_affiliation',
                      side_effect=BusinessException(Error.DATA_ALREADY_EXISTS, None)):
        rv = client.post('/api/v1/orgs/{}/affiliations'.format(org_id),
                         data=json.dumps(TestAffliationInfo.affliation1),
                         headers=headers,
                         content_type='application/json')
        assert rv.status_code == 400


def test_get_affiliations(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a list of affiliation for an org can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity_lear_mock),
                     headers=headers, content_type='application/json')
    rv = client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity_lear_mock2),
                     headers=headers, content_type='application/json')
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/affiliations'.format(org_id),
                     data=json.dumps(TestAffliationInfo.affiliation3),
                     headers=headers,
                     content_type='application/json')
    rv = client.post('/api/v1/orgs/{}/affiliations'.format(org_id),
                     data=json.dumps(TestAffliationInfo.affiliation4),
                     headers=headers,
                     content_type='application/json')

    rv = client.get('/api/v1/orgs/{}/affiliations'.format(org_id), headers=headers)
    assert rv.status_code == http_status.HTTP_200_OK
    affiliations = json.loads(rv.data)
    assert affiliations['entities'][0]['businessIdentifier'] == TestEntityInfo.entity_lear_mock['businessIdentifier']
    assert affiliations['entities'][1]['businessIdentifier'] == TestEntityInfo.entity_lear_mock2['businessIdentifier']


def test_search_orgs_for_affiliation(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that search org with affiliation works."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity_lear_mock),
                headers=headers, content_type='application/json')
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    client.post('/api/v1/orgs/{}/affiliations'.format(org_id), headers=headers,
                data=json.dumps(TestAffliationInfo.affiliation3), content_type='application/json')
    # Create a system token
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.get('/api/v1/orgs?affiliation={}'.format(TestAffliationInfo.affiliation3.get('businessIdentifier')),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    orgs = json.loads(rv.data)
    assert orgs.get('orgs')[0].get('name') == TestOrgInfo.org1.get('name')


def test_unauthorized_search_orgs_for_affiliation(client, jwt, session,
                                                  keycloak_mock):  # pylint:disable=unused-argument
    """Assert that search org with affiliation works."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    client.post('/api/v1/entities', data=json.dumps(TestEntityInfo.entity_lear_mock),
                headers=headers, content_type='application/json')
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    client.post('/api/v1/orgs/{}/affiliations'.format(org_id), headers=headers,
                data=json.dumps(TestAffliationInfo.affiliation3), content_type='application/json')
    # Create a system token
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_user_role)
    rv = client.get('/api/v1/orgs?affiliation={}'.format(TestAffliationInfo.affiliation3.get('businessIdentifier')),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_add_bcol_linked_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.bcol_linked()),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    assert rv.json.get('orgType') == OrgType.PREMIUM.value
    assert rv.json.get('name') == TestOrgInfo.bcol_linked()['name']


def test_add_bcol_linked_org_invalid_name(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.bcol_linked_invalid_name()),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST

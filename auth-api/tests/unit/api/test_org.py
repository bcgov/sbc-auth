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
from auth_api.utils.enums import AffidavitStatus, OrgType, OrgStatus
from tests.utilities.factory_scenarios import (
    TestAffidavit, TestAffliationInfo, TestContactInfo, TestEntityInfo, TestJwtClaims, TestOrgInfo)
from tests.utilities.factory_utils import factory_auth_header, factory_invitation, factory_invitation_anonymous


def test_add_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_search_org_by_client(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be searched."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED

    # system search
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.get('/api/v1/orgs?name={}'.format(TestOrgInfo.org1.get('name')),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    orgs = json.loads(rv.data)
    assert orgs.get('orgs')[0].get('name') == TestOrgInfo.org1.get('name')

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get('/api/v1/orgs?name={}'.format(TestOrgInfo.org1.get('name')),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    orgs = json.loads(rv.data)
    assert bool(orgs) is False

    rv = client.get('/api/v1/orgs?name={}'.format('notanexistingorgname'),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_204_NO_CONTENT

    # staff search
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get('/api/v1/orgs?name={}'.format(TestOrgInfo.org1.get('name')),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    orgs = json.loads(rv.data)
    assert orgs.get('orgs')[0].get('name') == TestOrgInfo.org1.get('name')

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get('/api/v1/orgs?status={}'.format('ACTIVE'),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    orgs = json.loads(rv.data)
    assert orgs.get('orgs')[0].get('name') == TestOrgInfo.org1.get('name')

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get('/api/v1/orgs?status={}&type={}'.format('ACTIVE', 'REGULAR'),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    orgs = json.loads(rv.data)
    assert orgs.get('orgs')[0].get('name') == TestOrgInfo.org1.get('name')


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

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
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
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
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

    # User will get a new role once the account is created
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
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

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
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

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)

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
    assert dictionary['members'][0]['membershipTypeCode'] == 'ADMIN'


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
    assert new_member['membershipTypeCode'] == 'USER'
    member_id = new_member['id']

    # Update the new member
    rv = client.patch('/api/v1/orgs/{}/members/{}'.format(org_id, member_id), headers=headers_invitee,
                      data=json.dumps({'role': 'COORDINATOR'}), content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['membershipTypeCode'] == 'COORDINATOR'

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
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


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
    assert new_member['membershipTypeCode'] == 'USER'
    member_id = new_member['id']

    # Update the new member
    rv = client.patch('/api/v1/orgs/{}/members/{}'.format(org_id, member_id), headers=headers_invitee,
                      data=json.dumps({'role': 'COORDINATOR'}), content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['membershipTypeCode'] == 'COORDINATOR'


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
    # Result is sorted desc order of created date
    assert affiliations['entities'][1]['businessIdentifier'] == TestEntityInfo.entity_lear_mock['businessIdentifier']
    assert affiliations['entities'][0]['businessIdentifier'] == TestEntityInfo.entity_lear_mock2['businessIdentifier']


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

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)

    org_search_response = client.get(f"/api/v1/orgs?name={TestOrgInfo.bcol_linked()['name']}",
                                     headers=headers, content_type='application/json')

    assert len(org_search_response.json.get('orgs')) == 1
    assert org_search_response.status_code == http_status.HTTP_200_OK
    orgs = json.loads(org_search_response.data)
    assert orgs.get('orgs')[0].get('name') == TestOrgInfo.bcol_linked()['name']
    account_id = orgs.get('orgs')[0].get('paymentSettings')[0].get('bcolAccountId')

    # do a search with bcol account id and name
    org_search_response = client.get(
        f"/api/v1/orgs?name={TestOrgInfo.bcol_linked()['name']}&bcolAccountId={account_id}",
        headers=headers, content_type='application/json')
    orgs = json.loads(org_search_response.data)
    assert orgs.get('orgs')[0].get('name') == TestOrgInfo.bcol_linked()['name']
    new_account_id = orgs.get('orgs')[0].get('paymentSettings')[0].get('bcolAccountId')
    assert account_id == new_account_id


def test_add_bcol_linked_org_failure_mailing_address(client, jwt, session,
                                                     keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.bcol_linked_incomplete_mailing_addrees()),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_add_bcol_linked_org_invalid_name(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.bcol_linked_invalid_name()),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_new_business_affiliation(client, jwt, session, keycloak_mock, nr_mock):  # pylint:disable=unused-argument
    """Assert that an NR can be affiliated to an org."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']

    rv = client.post('/api/v1/orgs/{}/affiliations?newBusiness=true'.format(org_id), headers=headers,
                     data=json.dumps(TestAffliationInfo.nr_affiliation), content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    assert dictionary['organization']['id'] == org_id
    assert dictionary['business']['businessIdentifier'] == TestAffliationInfo.nr_affiliation['businessIdentifier']


def test_get_org_admin_affidavits(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that staff admin can get pending affidavits."""
    # 1. Create User
    # 2. Get document signed link
    # 3. Create affidavit
    # 4. Create Org
    # 5. Get the affidavit as a bcol admin
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    document_signature = client.get('/api/v1/documents/test.jpeg/signatures', headers=headers,
                                    content_type='application/json')
    doc_key = document_signature.json.get('key')
    affidavit_response = client.post('/api/v1/users/{}/affidavits'.format(TestJwtClaims.public_user_role.get('sub')),
                                     headers=headers,
                                     data=json.dumps(TestAffidavit.get_test_affidavit_with_contact(doc_id=doc_key)),
                                     content_type='application/json')

    org_response = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_with_mailing_address()), headers=headers,
                               content_type='application/json')
    assert org_response.status_code == http_status.HTTP_201_CREATED

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)
    staff_response = client.get('/api/v1/orgs/{}/admins/affidavits'.format(org_response.json.get('id')),
                                headers=headers, content_type='application/json')
    assert staff_response.json.get('documentId') == doc_key
    assert staff_response.json.get('id') == affidavit_response.json.get('id')


def test_approve_org_with_pending_affidavits(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that staff admin can approve pending affidavits."""
    # 1. Create User
    # 2. Get document signed link
    # 3. Create affidavit
    # 4. Create Org
    # 5. Get the affidavit as a bcol admin
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    # POST a contact to test user
    client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact1),
                headers=headers, content_type='application/json')

    document_signature = client.get('/api/v1/documents/test.jpeg/signatures', headers=headers,
                                    content_type='application/json')
    doc_key = document_signature.json.get('key')
    affidavit_response = client.post('/api/v1/users/{}/affidavits'.format(TestJwtClaims.public_user_role.get('sub')),
                                     headers=headers,
                                     data=json.dumps(TestAffidavit.get_test_affidavit_with_contact(doc_id=doc_key)),
                                     content_type='application/json')

    org_response = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_with_mailing_address()), headers=headers,
                               content_type='application/json')
    assert org_response.status_code == http_status.HTTP_201_CREATED

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)

    org_patch_response = client.patch('/api/v1/orgs/{}/status'.format(org_response.json.get('id')),
                                      data=json.dumps({'statusCode': AffidavitStatus.APPROVED.value}),
                                      headers=headers, content_type='application/json')

    assert org_patch_response.json.get('orgStatus') == OrgStatus.ACTIVE.value

    staff_response = client.get('/api/v1/orgs/{}/admins/affidavits'.format(org_response.json.get('id')),
                                headers=headers, content_type='application/json')
    assert staff_response.json.get('documentId') == doc_key
    assert staff_response.json.get('id') == affidavit_response.json.get('id')
    assert staff_response.json.get('status') == AffidavitStatus.APPROVED.value


def test_search_orgs_with_pending_affidavits(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that staff admin can approve pending affidavits."""
    # 1. Create User
    # 2. Get document signed link
    # 3. Create affidavit
    # 4. Create Org
    # 5. Get the affidavit as a bcol admin
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    document_signature = client.get('/api/v1/documents/test.jpeg/signatures', headers=headers,
                                    content_type='application/json')
    doc_key = document_signature.json.get('key')
    client.post('/api/v1/users/{}/affidavits'.format(TestJwtClaims.public_user_role.get('sub')),
                headers=headers,
                data=json.dumps(TestAffidavit.get_test_affidavit_with_contact(doc_id=doc_key)),
                content_type='application/json')

    org_response = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_with_mailing_address()), headers=headers,
                               content_type='application/json')
    assert org_response.status_code == http_status.HTTP_201_CREATED

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)

    org_search_response = client.get('/api/v1/orgs?status=PENDING_AFFIDAVIT_REVIEW',
                                     headers=headers, content_type='application/json')

    assert len(org_search_response.json.get('orgs')) == 1


def test_search_org_pagination(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that pagination works."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                headers=headers, content_type='application/json')
    client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org2),
                headers=headers, content_type='application/json')
    client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org3),
                headers=headers, content_type='application/json')

    # staff search
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get('/api/v1/orgs?page=1&limit=10',
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    orgs = json.loads(rv.data)
    assert orgs.get('total') == 3
    assert len(orgs.get('orgs')) == 3

    rv = client.get('/api/v1/orgs?page=1&limit=2',
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    orgs = json.loads(rv.data)
    assert orgs.get('total') == 3
    assert len(orgs.get('orgs')) == 2


def test_search_org_invitations(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that pagination works."""
    # Create 2 anonymous org invitations
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_dir_search_role)
    client.post('/api/v1/users', headers=headers, content_type='application/json')

    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_anonymous),
                     headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    client.post('/api/v1/invitations', data=json.dumps(factory_invitation_anonymous(org_id=org_id)),
                headers=headers, content_type='application/json')

    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_anonymous_2),
                     headers=headers, content_type='application/json')
    dictionary = json.loads(rv.data)
    org_id = dictionary['id']
    client.post('/api/v1/invitations', data=json.dumps(factory_invitation_anonymous(org_id=org_id)),
                headers=headers, content_type='application/json')

    # staff search
    rv = client.get('/api/v1/orgs?status={}'.format(OrgStatus.PENDING_ACTIVATION.value),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    orgs = json.loads(rv.data)
    assert len(orgs.get('orgs')) == 2
    assert len(orgs.get('orgs')[0].get('invitations')) == 1

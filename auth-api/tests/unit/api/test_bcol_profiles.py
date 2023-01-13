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

"""Tests to verify the bcol-profiles  API end-point.

Test-Suite to ensure that the /accounts endpoint is working as expected.
"""

import copy
import json

from auth_api import status as http_status
from auth_api.schemas import utils as schema_utils
from auth_api.utils.enums import OrgStatus
from tests.utilities.factory_scenarios import TestBCOLInfo, TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_auth_header, factory_org_model


def test_bcol_profiles_returns_200(app, client, jwt, session):  # pylint:disable=unused-argument
    """Assert bcol profile creation."""
    claims = copy.deepcopy(TestJwtClaims.public_user_role.value)

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.post('/api/v1/bcol-profiles', data=json.dumps(TestOrgInfo.bcol_linked().get('bcOnlineCredential')),
                     headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'bconline_response')[0]


def test_bcol_id_already_linked(client, jwt, session):
    """Assert bcol id conflict validation."""
    claims = copy.deepcopy(TestJwtClaims.public_user_role.value)
    headers = factory_auth_header(jwt=jwt, claims=claims)

    rv = client.post('/api/v1/bcol-profiles', data=json.dumps(TestOrgInfo.bcol_linked().get('bcOnlineCredential')),
                     headers=headers, content_type='application/json')

    bcol_org = factory_org_model(org_info=TestOrgInfo.org3, bcol_info=TestOrgInfo.bcol_linked())
    bcol_org.bcol_account_id = rv.json['accountNumber']
    bcol_org.save()

    rv_duplicate = client.post('/api/v1/bcol-profiles', data=json.dumps(TestOrgInfo.bcol_linked().get('bcOnlineCredential')),
                               headers=headers, content_type='application/json')
    assert rv_duplicate.status_code == http_status.HTTP_409_CONFLICT


def test_bcol_id_already_linked_to_rejected(client, jwt, session):
    """Assert rejected bcol id does not conflict."""
    claims = copy.deepcopy(TestJwtClaims.public_user_role.value)
    headers = factory_auth_header(jwt=jwt, claims=claims)

    rv = client.post('/api/v1/bcol-profiles', data=json.dumps(TestOrgInfo.bcol_linked().get('bcOnlineCredential')),
                     headers=headers, content_type='application/json')

    bcol_org = factory_org_model(org_info=TestOrgInfo.org3, bcol_info=TestOrgInfo.bcol_linked())
    bcol_org.bcol_account_id = rv.json['accountNumber']
    bcol_org.status_code = OrgStatus.REJECTED.value
    bcol_org.save()

    rv_duplicate = client.post('/api/v1/bcol-profiles', data=json.dumps(TestOrgInfo.bcol_linked().get('bcOnlineCredential')),
                               headers=headers, content_type='application/json')
    assert rv_duplicate.status_code == http_status.HTTP_200_OK

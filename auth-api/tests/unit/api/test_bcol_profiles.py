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
# See the License for the specific language governing permissions
# limitations under the License.

"""Tests to verify the bcol-profiles  API end-point.

Test-Suite to ensure that the /accounts endpoint is working as expected.
"""

import copy
import json

from auth_api import status as http_status
from tests.utilities.factory_scenarios import TestJwtClaims
from tests.utilities.factory_utils import (
    TestOrgInfo, factory_auth_header)


def test_bcol_profiles_returns_200(app, client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for product returns 200."""
    claims = copy.deepcopy(TestJwtClaims.public_user_role.value)

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.post('/api/v1/bcol-profiles', data=json.dumps(TestOrgInfo.bcol_linked().get('bcOnlineCredential')),
                     headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK

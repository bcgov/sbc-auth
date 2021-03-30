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
"""Tests to verify the Staff Tasks API end-point.

Test-Suite to ensure that the /staff-tasks endpoint is working as expected.
"""

from unittest.mock import patch

from auth_api import status as http_status
from auth_api.schemas import utils as schema_utils
from tests.utilities.factory_utils import factory_auth_header
from tests.utilities.factory_scenarios import TestJwtClaims


def test_fetch_staff_tasks(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the staff tasks can be fetched."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.get('/api/v1/staff-tasks', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK

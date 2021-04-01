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
"""Tests to verify the Tasks API end-point.

Test-Suite to ensure that the /tasks endpoint is working as expected.
"""

from auth_api import status as http_status
from tests.utilities.factory_utils import (factory_auth_header,
                                           factory_task_service)
from tests.utilities.factory_scenarios import TestJwtClaims
from auth_api.schemas import utils as schema_utils


def test_fetch_tasks(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the tasks can be fetched."""
    factory_task_service()
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/tasks', headers=headers, content_type='application/json')
    item_list = rv.json
    assert schema_utils.validate(item_list, 'task_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK

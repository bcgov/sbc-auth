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
                                           factory_task_service, factory_user_model)
from tests.utilities.factory_scenarios import TestJwtClaims, KeycloakScenario
from auth_api.schemas import utils as schema_utils
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.enums import TaskRelationshipType

KEYCLOAK_SERVICE = KeycloakService()


def test_fetch_tasks(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the tasks can be fetched."""
    # request = KeycloakScenario.create_user_request()
    # KEYCLOAK_SERVICE.add_user(request, return_if_exists=True)
    # user = KEYCLOAK_SERVICE.get_user_by_username(request.user_name)
    # user_id = user.id
    # headers_invitee = factory_auth_header(jwt=jwt, claims=TestJwtClaims.get_test_user(user_id, source='BCSC'))
    # client.post('/api/v1/users', headers=headers_invitee, content_type='application/json')

    user = factory_user_model()
    factory_task_service(user.id)
    task_relationship_type = TaskRelationshipType.ORG.value

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/tasks/{}'.format(task_relationship_type), headers=headers, content_type='application/json')
    item_list = rv.json
    assert schema_utils.validate(item_list, 'task_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK

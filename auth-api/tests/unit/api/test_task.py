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

import json
from auth_api import status as http_status
from tests.utilities.factory_utils import (factory_auth_header,
                                           factory_task_service, factory_user_model)
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo, TestContactInfo, TestAffidavit
from auth_api.schemas import utils as schema_utils
from auth_api.utils.enums import TaskRelationshipType, TaskStatus, TaskType, AffidavitStatus, OrgStatus


def test_fetch_tasks(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the tasks can be fetched."""
    user = factory_user_model()
    factory_task_service(user.id)
    task_type = TaskRelationshipType.ORG.value

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/tasks?type={}'.format(task_type), headers=headers, content_type='application/json')
    item_list = rv.json
    assert schema_utils.validate(item_list, 'task_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK


def test_fetch_tasks_with_status(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the tasks can be fetched."""
    user = factory_user_model()
    factory_task_service(user.id)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/tasks?type=ORG&status=OPEN', headers=headers, content_type='application/json')
    item_list = rv.json
    assert schema_utils.validate(item_list, 'task_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK


def test_put_task(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that the task can be updated."""
    # 1. Create User
    # 2. Get document signed link
    # 3. Create affidavit
    # 4. Create Org
    # 5. Update the created task and the relationship

    bc_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post('/api/v1/users', headers=bc_headers, content_type='application/json')
    # POST a contact to test user
    client.post('/api/v1/users/contacts', data=json.dumps(TestContactInfo.contact1),
                headers=bc_headers, content_type='application/json')

    document_signature = client.get('/api/v1/documents/test.jpeg/signatures', headers=bc_headers,
                                    content_type='application/json')
    doc_key = document_signature.json.get('key')
    client.post('/api/v1/users/{}/affidavits'.format(TestJwtClaims.public_user_role.get('sub')),
                headers=bc_headers,
                data=json.dumps(TestAffidavit.get_test_affidavit_with_contact(doc_id=doc_key)),
                content_type='application/json')

    org_response = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_with_mailing_address()),
                               headers=bc_headers,
                               content_type='application/json')
    assert org_response.status_code == http_status.HTTP_201_CREATED
    org_id = org_response.json.get('id')

    update_task_payload = {
        'id': 1,
        'name': 'bar',
        'dateSubmitted': '2020-11-23T15:14:20.712096+00:00',
        'relationshipType': TaskRelationshipType.ORG.value,
        'relationshipId': org_id,
        'type': TaskType.PENDING_STAFF_REVIEW.value,
        'status': TaskStatus.COMPLETED.value,
        'relationshipStatus': AffidavitStatus.APPROVED.value
    }

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.put('/api/v1/tasks/{}'.format(1),
                    data=json.dumps(update_task_payload),
                    headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    assert rv.status_code == http_status.HTTP_200_OK
    assert dictionary['status'] == TaskStatus.COMPLETED.value

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get('/api/v1/orgs/{}'.format(org_id),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['id'] == org_id
    assert rv.json.get('orgStatus') == OrgStatus.ACTIVE.value

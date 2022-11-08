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

import pytest

from auth_api import status as http_status
from auth_api.models.dataclass import TaskSearch
from auth_api.models import ProductCode as ProductCodeModel
from auth_api.schemas import utils as schema_utils
from auth_api.services import Affidavit as AffidavitService
from auth_api.services import Org as OrgService
from auth_api.services import Task as TaskService
from auth_api.utils.enums import (
    AccessType, OrgStatus, ProductSubscriptionStatus, TaskAction, TaskRelationshipStatus, TaskRelationshipType,
    TaskStatus, TaskTypePrefix)
from tests.utilities.factory_scenarios import (
    TestAffidavit, TestJwtClaims, TestOrgInfo, TestOrgProductsInfo, TestUserInfo)
from tests.utilities.factory_utils import (
    factory_auth_header, factory_task_service, factory_user_model, factory_user_model_with_contact, patch_token_info)


def test_fetch_tasks(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the tasks can be fetched."""
    user = factory_user_model()
    factory_task_service(user.id)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/tasks', headers=headers, content_type='application/json')
    item_list = rv.json
    assert schema_utils.validate(item_list, 'paged_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK


def test_fetch_tasks_no_content(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the none can be fetched."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/tasks', headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK


@pytest.mark.parametrize('test_name, endpoint', [
    ('status', 'status=OPEN'),
    ('relationshipStatus', 'relationshipStatus=PENDING_STAFF_REVIEW'),
    ('dateSubmitted', 'endDate=2022-10-20'),
    ('dateSubmitted', 'startDate=2022-10-20'),
    ('type', 'type=New Account'),
    ('name', 'name=foo'),
    ('modifiedBy', 'modifiedBy=User'),
])
def test_fetch_tasks_with_params(test_name, client, jwt, endpoint, session):  # pylint:disable=unused-argument
    """Assert that the tasks can be fetched."""
    user = factory_user_model()
    factory_task_service(user.id)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get(f'/api/v1/tasks?{endpoint}',
                    headers=headers, content_type='application/json')
    item_list = rv.json
    assert item_list['tasks']
    assert len(item_list['tasks']) > 0
    assert item_list['tasks'][0][test_name]
    assert schema_utils.validate(item_list, 'paged_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK


@pytest.mark.parametrize('test_name, endpoint', [
    ('with-2-params', 'status=OPEN&relationshipStatus=PENDING_STAFF_REVIEW'),
    ('with-many-params', 'status=OPEN&relationshipStatus=PENDING_STAFF_REVIEW&page=1&limit=10')
])
def test_fetch_tasks_with_many_params(test_name, client, jwt, endpoint, session):
    """Assert that the tasks can be fetched."""
    user = factory_user_model()
    factory_task_service(user.id)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get(f'/api/v1/tasks?{endpoint}',
                    headers=headers, content_type='application/json')
    item_list = rv.json
    assert item_list['tasks']
    assert len(item_list['tasks']) > 0
    assert item_list['tasks'][0]['relationshipStatus']
    assert schema_utils.validate(item_list, 'paged_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK


def test_put_task_org(client, jwt, session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that the task can be updated."""
    # 1. Create User
    # 2. Get document signed link
    # 3. Create affidavit
    # 4. Create Org
    # 5. Update the created task and the relationship
    monkeypatch.setattr('auth_api.utils.user_context._get_token_info', lambda: TestJwtClaims.public_bceid_user)
    user_with_token = TestUserInfo.user_staff_admin
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_user_role['idp_userid']
    user = factory_user_model_with_contact(user_with_token)

    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(affidavit_info=affidavit_info)

    org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id)
    org_dict = org.as_dict()
    assert org_dict['org_status'] == OrgStatus.PENDING_STAFF_REVIEW.value
    org_id = org_dict['id']

    task_search = TaskSearch(
        status=[TaskStatus.OPEN.value],
        page=1,
        limit=10
    )
    tasks = TaskService.fetch_tasks(task_search)
    fetched_tasks = tasks['tasks']
    fetched_task = fetched_tasks[0]

    task_type_new_account = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
    assert fetched_task['type'] == task_type_new_account

    update_task_payload = {
        'status': TaskStatus.COMPLETED.value,
        'relationshipStatus': TaskRelationshipStatus.ACTIVE.value
    }

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.put('/api/v1/tasks/{}'.format(fetched_task['id']),
                    data=json.dumps(update_task_payload),
                    headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    assert rv.status_code == http_status.HTTP_200_OK
    assert dictionary['status'] == TaskStatus.COMPLETED.value
    assert dictionary['relationshipStatus'] == TaskRelationshipStatus.ACTIVE.value

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get('/api/v1/orgs/{}'.format(org_id),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['id'] == org_id
    assert rv.json.get('orgStatus') == OrgStatus.ACTIVE.value


def test_put_task_org_on_hold(client, jwt, session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that the task can be updated."""
    # 1. Create User
    # 2. Get document signed link
    # 3. Create affidavit
    # 4. Create Org
    # 5. Update the created task and the relationship
    monkeypatch.setattr('auth_api.utils.user_context._get_token_info', lambda: TestJwtClaims.public_bceid_user)
    user_with_token = TestUserInfo.user_bceid_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_user_role['idp_userid']
    user = factory_user_model_with_contact(user_with_token)

    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(affidavit_info=affidavit_info)

    org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id)
    org_dict = org.as_dict()
    assert org_dict['org_status'] == OrgStatus.PENDING_STAFF_REVIEW.value
    org_id = org_dict['id']

    task_search = TaskSearch(
        status=[TaskStatus.OPEN.value],
        page=1,
        limit=10
    )

    tasks = TaskService.fetch_tasks(task_search)
    fetched_tasks = tasks['tasks']
    fetched_task = fetched_tasks[0]

    task_type_new_account = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
    assert fetched_task['type'] == task_type_new_account

    update_task_payload = {
        'status': TaskStatus.HOLD.value,
        'relationshipStatus': TaskRelationshipStatus.PENDING_STAFF_REVIEW.value,
        'remarks': ['AFFIDAVIT SEAL MISSING']
    }

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.put('/api/v1/tasks/{}'.format(fetched_task['id']),
                    data=json.dumps(update_task_payload),
                    headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    assert rv.status_code == http_status.HTTP_200_OK
    assert dictionary['status'] == TaskStatus.HOLD.value
    assert dictionary['relationshipStatus'] == TaskRelationshipStatus.PENDING_STAFF_REVIEW.value

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get('/api/v1/orgs/{}'.format(org_id),
                    headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    dictionary = json.loads(rv.data)
    assert dictionary['id'] == org_id
    assert rv.json.get('orgStatus') == OrgStatus.PENDING_STAFF_REVIEW.value


def test_put_task_product(client, jwt, session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that the task can be updated."""
    # 1. Create User
    # 4. Create Product subscription
    # 5. Update the created task and the relationship

    # Post user, org and product subscription
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    user_with_token = TestUserInfo.user_staff_admin
    user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
    user_with_token['idp_userid'] = TestJwtClaims.public_user_role['idp_userid']
    user = factory_user_model_with_contact(user_with_token)

    patch_token_info({
        'sub': str(user_with_token['keycloak_guid']),
        'idp_userid': str(user_with_token['idp_userid']),
        'username': 'public_user',
        'realm_access': {
            'roles': [
                'edit'
            ]
        }
    }, monkeypatch)

    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(affidavit_info=affidavit_info)

    patch_token_info(TestJwtClaims.public_bceid_user, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id)
    org_dict = org.as_dict()

    product_which_doesnt_need_approval = TestOrgProductsInfo.org_products1
    rv_products = client.post(f"/api/v1/orgs/{org_dict.get('id')}/products",
                              data=json.dumps(product_which_doesnt_need_approval),
                              headers=headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    task_search = TaskSearch(
        status=[TaskStatus.OPEN.value],
        page=1,
        limit=10
    )

    tasks = TaskService.fetch_tasks(task_search)
    assert len(tasks['tasks']) == 1

    product_which_needs_approval = TestOrgProductsInfo.org_products_vs
    rv_products = client.post(f"/api/v1/orgs/{org_dict.get('id')}/products",
                              data=json.dumps(product_which_needs_approval),
                              headers=headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    tasks = TaskService.fetch_tasks(task_search)
    fetched_tasks = tasks['tasks']
    fetched_task = fetched_tasks[1]
    assert fetched_task['relationship_type'] == TaskRelationshipType.PRODUCT.value

    # Assert task name
    product: ProductCodeModel = ProductCodeModel.find_by_code(
        product_which_needs_approval['subscriptions'][0].get('productCode'))
    org_name = org_dict['name']
    assert fetched_task['name'] == org_name
    assert fetched_task['type'] == product.description

    # Assert the task can be updated and the product status is changed to active
    update_task_payload = {
        'relationshipStatus': ProductSubscriptionStatus.ACTIVE.value
    }

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.put('/api/v1/tasks/{}'.format(fetched_task['id']),
                    data=json.dumps(update_task_payload),
                    headers=headers, content_type='application/json')

    dictionary = json.loads(rv.data)
    assert rv.status_code == http_status.HTTP_200_OK
    assert dictionary['status'] == TaskStatus.COMPLETED.value
    assert dictionary['relationshipStatus'] == TaskRelationshipStatus.ACTIVE.value


def test_fetch_task(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the task can be fetched by id."""
    user = factory_user_model()
    task = factory_task_service(user.id)
    task_id = task._model.id

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/tasks/{}'.format(task_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('name') == task._model.name


@pytest.mark.parametrize('user_token, access_type, expected_task_action', [
    (TestJwtClaims.public_bceid_user, AccessType.EXTRA_PROVINCIAL.value, TaskAction.AFFIDAVIT_REVIEW.value),
    (TestJwtClaims.public_bceid_user, AccessType.REGULAR_BCEID.value, TaskAction.AFFIDAVIT_REVIEW.value),
    (TestJwtClaims.public_bceid_user, AccessType.GOVN.value, TaskAction.AFFIDAVIT_REVIEW.value),
    (TestJwtClaims.public_user_role, AccessType.GOVN.value, TaskAction.ACCOUNT_REVIEW.value),
])
def test_tasks_on_account_creation(client, jwt, session, keycloak_mock,  # pylint:disable=unused-argument
                                   monkeypatch, user_token, access_type, expected_task_action):
    """Assert that tasks are created."""
    # 1. Create User
    # 2. Get document signed link
    # 3. Create affidavit
    # 4. Create Org
    # 5. Assert correct task is created

    monkeypatch.setattr('auth_api.utils.user_context._get_token_info', lambda: user_token)
    user = factory_user_model_with_contact(user_token, keycloak_guid=user_token['sub'])

    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(affidavit_info=affidavit_info)

    org_info = TestOrgInfo.org_with_mailing_address()
    org_info['accessType'] = access_type
    OrgService.create_org(org_info, user_id=user.id)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.get('/api/v1/tasks', headers=headers, content_type='application/json')
    assert rv.json['tasks'][0]['action'] == expected_task_action

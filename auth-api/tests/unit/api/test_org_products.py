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

import pytest

from auth_api import status as http_status
from auth_api.schemas import utils as schema_utils
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo, TestOrgProductsInfo
from tests.utilities.factory_utils import factory_auth_header


def test_add_multiple_org_products(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(TestOrgProductsInfo.org_products2),
                              headers=headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]


def test_add_single_org_product(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(TestOrgProductsInfo.org_products1),
                              headers=headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]


def test_add_single_org_product_vs(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org1),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(TestOrgProductsInfo.org_products_vs),
                              headers=headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    rv_products = client.get(f"/api/v1/orgs/{dictionary.get('id')}/products", headers=headers,
                             content_type='application/json')
    list_products = json.loads(rv_products.data)
    vs_product = next(prod for prod in list_products if prod.get('code') == 'VS')
    assert vs_product.get('subscriptionStatus') == 'PENDING_STAFF_REVIEW'


def test_dir_search_doesnt_get_any_product(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert dir search doesnt get any active product subscriptions."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_anonymous),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    assert dictionary['accessType'] == 'ANONYMOUS'
    assert schema_utils.validate(rv.json, 'org_response')[0]

    rv_products = client.get(f"/api/v1/orgs/{dictionary.get('id')}/products", headers=headers,
                             content_type='application/json')

    list_products = json.loads(rv_products.data)
    assert len([x for x in list_products if x.get('subscriptionStatus') != 'NOT_SUBSCRIBED']) == 0


def test_new_dir_search_can_be_returned(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert new dir search product subscriptions can be subscribed to via system admin / returned via org user."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv = client.post('/api/v1/orgs',
                     data=json.dumps(TestOrgInfo.org1),
                     headers=headers,
                     content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)
    system_admin_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_admin_role)
    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(TestOrgProductsInfo.org_products_nds),
                              headers=system_admin_headers,
                              content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    rv_products = client.get(f"/api/v1/orgs/{dictionary.get('id')}/products?include_hidden=true",
                             headers=headers,
                             content_type='application/json')
    list_products = json.loads(rv_products.data)
    nds_product = next(prod for prod in list_products if prod.get('code') == 'NDS')
    assert nds_product.get('subscriptionStatus') == 'ACTIVE'


def assert_product_parent_and_child_statuses(client, jwt, org_id,
                                             parent_code, parent_status, child_code, child_status):
    """Assert that an organizations parent product code and child product code have the expected statuses."""
    staff_view_account_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_view_accounts_role)
    rv_products = client.get(f'/api/v1/orgs/{org_id}/products', headers=staff_view_account_headers,
                             content_type='application/json')
    list_products = json.loads(rv_products.data)

    mhr_product = next(prod for prod in list_products
                       if prod.get('code') == child_code)

    parent_mhr_product = next(prod for prod in list_products if prod.get('code') == parent_code)

    assert mhr_product.get('subscriptionStatus') == child_status
    assert parent_mhr_product.get('subscriptionStatus') == parent_status


@pytest.mark.parametrize('org_product_info', [
    TestOrgProductsInfo.mhr_qs_lawyer_and_notaries,
    TestOrgProductsInfo.mhr_qs_home_manufacturers,
    TestOrgProductsInfo.mhr_qs_home_dealers
])
def test_add_single_org_product_mhr_qualified_supplier_approve(client, jwt, session, keycloak_mock, org_product_info):
    """Assert that MHR sub products subscriptions can be created and approved."""
    # setup user and org
    staff_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=user_headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_premium),
                     headers=user_headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)

    # Create product subscription
    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(org_product_info),
                              headers=user_headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    # Fetch org products and validate subscription status
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'PENDING_STAFF_REVIEW',
                                             org_product_info['subscriptions'][0]['productCode'],
                                             'PENDING_STAFF_REVIEW')

    # Should show up as a review task for staff
    rv = client.get('/api/v1/tasks', headers=staff_headers, content_type='application/json')

    item_list = rv.json
    assert schema_utils.validate(item_list, 'paged_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK
    assert len(item_list['tasks']) == 1

    task = item_list['tasks'][0]
    assert task['relationshipStatus'] == 'PENDING_STAFF_REVIEW'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == org_product_info['subscriptions'][0]['externalSourceId']

    # Approve task
    rv = client.put('/api/v1/tasks/{}'.format(task['id']),
                    data=json.dumps({'relationshipStatus': 'ACTIVE'}),
                    headers=staff_headers, content_type='application/json')

    task = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert task['relationshipStatus'] == 'ACTIVE'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == org_product_info['subscriptions'][0]['externalSourceId']

    # MHR parent and sub product should be active
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'ACTIVE',
                                             org_product_info['subscriptions'][0]['productCode'], 'ACTIVE')


@pytest.mark.parametrize('org_product_info', [
    TestOrgProductsInfo.mhr_qs_lawyer_and_notaries,
    TestOrgProductsInfo.mhr_qs_home_manufacturers,
    TestOrgProductsInfo.mhr_qs_home_dealers
])
def test_add_single_org_product_mhr_qualified_supplier_reject(client, jwt, session, keycloak_mock, org_product_info):
    """Assert that MHR sub products subscriptions can be created and rejected with no pre-existing subscriptions."""
    # setup user and org
    staff_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=user_headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_premium),
                     headers=user_headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)

    # Create product subscription
    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(org_product_info),
                              headers=user_headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    # Fetch org products and validate subscription status
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'PENDING_STAFF_REVIEW',
                                             org_product_info['subscriptions'][0]['productCode'],
                                             'PENDING_STAFF_REVIEW')

    # Should show up as a review task for staff
    rv = client.get('/api/v1/tasks', headers=staff_headers, content_type='application/json')

    item_list = rv.json
    assert schema_utils.validate(item_list, 'paged_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK
    assert len(item_list['tasks']) == 1

    task = item_list['tasks'][0]
    assert task['relationshipStatus'] == 'PENDING_STAFF_REVIEW'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == org_product_info['subscriptions'][0]['externalSourceId']

    # Reject task
    rv = client.put('/api/v1/tasks/{}'.format(task['id']),
                    data=json.dumps({'relationshipStatus': 'REJECTED'}),
                    headers=staff_headers, content_type='application/json')

    task = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert task['relationshipStatus'] == 'REJECTED'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == org_product_info['subscriptions'][0]['externalSourceId']

    # MHR parent and sub product should be rejected
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'REJECTED',
                                             org_product_info['subscriptions'][0]['productCode'], 'REJECTED')


@pytest.mark.parametrize('org_product_info', [
    TestOrgProductsInfo.mhr_qs_lawyer_and_notaries,
    TestOrgProductsInfo.mhr_qs_home_manufacturers,
    TestOrgProductsInfo.mhr_qs_home_dealers
])
def test_add_single_org_product_mhr_qualified_supplier_reject2(client, jwt, session, keycloak_mock, org_product_info):
    """Assert that MHR sub products subscriptions can be created and rejected when a parent product already exists."""
    # setup user and org
    staff_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=user_headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_premium),
                     headers=user_headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)

    # Create parent product subscription
    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(TestOrgProductsInfo.mhr),
                              headers=user_headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    # Fetch org products and validate subscription status
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'ACTIVE',
                                             org_product_info['subscriptions'][0]['productCode'],
                                             'NOT_SUBSCRIBED')

    # Create sub product subscription
    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(org_product_info),
                              headers=user_headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    # Fetch org products and validate subscription status
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'ACTIVE',
                                             org_product_info['subscriptions'][0]['productCode'],
                                             'PENDING_STAFF_REVIEW')

    # Should show up as a review task for staff
    rv = client.get('/api/v1/tasks', headers=staff_headers, content_type='application/json')

    item_list = rv.json
    assert schema_utils.validate(item_list, 'paged_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK
    assert len(item_list['tasks']) == 1

    task = item_list['tasks'][0]
    assert task['relationshipStatus'] == 'PENDING_STAFF_REVIEW'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == org_product_info['subscriptions'][0]['externalSourceId']

    # Reject task
    rv = client.put('/api/v1/tasks/{}'.format(task['id']),
                    data=json.dumps({'relationshipStatus': 'REJECTED'}),
                    headers=staff_headers, content_type='application/json')

    task = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert task['relationshipStatus'] == 'REJECTED'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == org_product_info['subscriptions'][0]['externalSourceId']

    # MHR parent and sub product should be rejected
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'ACTIVE',
                                             org_product_info['subscriptions'][0]['productCode'], 'REJECTED')


def test_add_org_product_mhr_qualified_supplier_reject_approve(client, jwt, session, keycloak_mock):
    """Assert that MHR sub products subscriptions can be rejected and approved after with a different sub product."""
    # setup user and org
    staff_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=user_headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_premium),
                     headers=user_headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)

    qsln_product_info = TestOrgProductsInfo.mhr_qs_lawyer_and_notaries
    qshm_product_info = TestOrgProductsInfo.mhr_qs_home_manufacturers

    # Create first sub product subscription
    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(qsln_product_info),
                              headers=user_headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    # Fetch org products and validate subscription status
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'PENDING_STAFF_REVIEW',
                                             qsln_product_info['subscriptions'][0]['productCode'],
                                             'PENDING_STAFF_REVIEW')

    # Should show up as a review task for staff
    rv = client.get('/api/v1/tasks', headers=staff_headers, content_type='application/json')

    item_list = rv.json
    assert schema_utils.validate(item_list, 'paged_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK
    assert len(item_list['tasks']) == 1

    task = item_list['tasks'][0]
    assert task['relationshipStatus'] == 'PENDING_STAFF_REVIEW'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == qsln_product_info['subscriptions'][0]['externalSourceId']

    # Reject task
    rv = client.put('/api/v1/tasks/{}'.format(task['id']),
                    data=json.dumps({'relationshipStatus': 'REJECTED'}),
                    headers=staff_headers, content_type='application/json')

    task = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert task['relationshipStatus'] == 'REJECTED'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == qsln_product_info['subscriptions'][0]['externalSourceId']

    # MHR parent and sub product should be rejected
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'REJECTED',
                                             qsln_product_info['subscriptions'][0]['productCode'], 'REJECTED')

    # Create second sub product subscription
    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(qshm_product_info),
                              headers=user_headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    # Fetch org products and validate subscription status
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'PENDING_STAFF_REVIEW',
                                             qshm_product_info['subscriptions'][0]['productCode'],
                                             'PENDING_STAFF_REVIEW')

    # Should show up as a review task for staff
    rv = client.get('/api/v1/tasks', headers=staff_headers, content_type='application/json')

    item_list = rv.json
    assert schema_utils.validate(item_list, 'paged_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK
    assert len(item_list['tasks']) == 2

    task = item_list['tasks'][1]
    assert task['relationshipStatus'] == 'PENDING_STAFF_REVIEW'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == qshm_product_info['subscriptions'][0]['externalSourceId']

    # Approve task
    rv = client.put('/api/v1/tasks/{}'.format(task['id']),
                    data=json.dumps({'relationshipStatus': 'ACTIVE'}),
                    headers=staff_headers, content_type='application/json')

    task = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert task['relationshipStatus'] == 'ACTIVE'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == qshm_product_info['subscriptions'][0]['externalSourceId']

    # MHR parent and sub product should be approved
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'ACTIVE',
                                             qshm_product_info['subscriptions'][0]['productCode'], 'ACTIVE')


def test_org_product_resubmission_invalid(client, jwt, session, keycloak_mock):
    """Assert that product subscription re-submission returns invalid for unsupported products."""
    # setup user and org
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=user_headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_premium),
                     headers=user_headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)

    product_info = TestOrgProductsInfo.org_products_vs

    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(product_info),
                              headers=user_headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    rv_products = client.get(f"/api/v1/orgs/{dictionary.get('id')}/products", headers=user_headers,
                             content_type='application/json')
    list_products = json.loads(rv_products.data)
    product = next(prod for prod in list_products if
                   prod.get('code') == product_info['subscriptions'][0]['productCode'])
    assert product.get('subscriptionStatus') == 'PENDING_STAFF_REVIEW'

    # Should return bad request for invalid product for products without can_resubmit flag True
    rv_products = client.patch(f"/api/v1/orgs/{dictionary.get('id')}/products",
                               data=json.dumps(product_info),
                               headers=user_headers, content_type='application/json')

    assert rv_products.status_code == http_status.HTTP_400_BAD_REQUEST
    error = rv_products.json
    assert error['message'] == 'Product is not valid for re-submission.'


def test_org_product_resubmission_state_invalid(client, jwt, session, keycloak_mock):
    """Assert that product subscription re-submission returns invalid state."""
    # setup user and org
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=user_headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_premium),
                     headers=user_headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)

    product_info = TestOrgProductsInfo.mhr_qs_lawyer_and_notaries

    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(product_info),
                              headers=user_headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    rv_products = client.get(f"/api/v1/orgs/{dictionary.get('id')}/products", headers=user_headers,
                             content_type='application/json')
    list_products = json.loads(rv_products.data)
    product = next(prod for prod in list_products if
                   prod.get('code') == product_info['subscriptions'][0]['productCode'])
    assert product.get('subscriptionStatus') == 'PENDING_STAFF_REVIEW'

    # Should return bad request for invalid product for products not in REJECTED state
    rv_products = client.patch(f"/api/v1/orgs/{dictionary.get('id')}/products",
                               data=json.dumps(product_info),
                               headers=user_headers, content_type='application/json')

    assert rv_products.status_code == http_status.HTTP_400_BAD_REQUEST
    error = rv_products.json
    assert error['message'] == 'Product is not in a valid state for re-submission.'


def test_org_product_resubmission(client, jwt, session, keycloak_mock):
    """Assert that product subscription re-submission works properly."""
    # setup user and org
    staff_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/users', headers=user_headers, content_type='application/json')
    rv = client.post('/api/v1/orgs', data=json.dumps(TestOrgInfo.org_premium),
                     headers=user_headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED
    dictionary = json.loads(rv.data)

    qsln_product_info = TestOrgProductsInfo.mhr_qs_lawyer_and_notaries

    # Create first sub product subscription
    rv_products = client.post(f"/api/v1/orgs/{dictionary.get('id')}/products",
                              data=json.dumps(qsln_product_info),
                              headers=user_headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_201_CREATED
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    # Fetch org products and validate subscription status
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'PENDING_STAFF_REVIEW',
                                             qsln_product_info['subscriptions'][0]['productCode'],
                                             'PENDING_STAFF_REVIEW')

    # Should show up as a review task for staff
    rv = client.get('/api/v1/tasks', headers=staff_headers, content_type='application/json')

    item_list = rv.json
    assert schema_utils.validate(item_list, 'paged_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK
    assert len(item_list['tasks']) == 1

    task = item_list['tasks'][0]
    assert task['relationshipStatus'] == 'PENDING_STAFF_REVIEW'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == qsln_product_info['subscriptions'][0]['externalSourceId']

    # Reject task
    rv = client.put('/api/v1/tasks/{}'.format(task['id']),
                    data=json.dumps({'relationshipStatus': 'REJECTED'}),
                    headers=staff_headers, content_type='application/json')

    task = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert task['relationshipStatus'] == 'REJECTED'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == qsln_product_info['subscriptions'][0]['externalSourceId']

    # MHR parent and sub product should be rejected
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'REJECTED',
                                             qsln_product_info['subscriptions'][0]['productCode'], 'REJECTED')

    # Resubmit sub product subscription
    rv_products = client.patch(f"/api/v1/orgs/{dictionary.get('id')}/products",
                               data=json.dumps(qsln_product_info),
                               headers=user_headers, content_type='application/json')
    assert rv_products.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv_products.json, 'org_product_subscriptions_response')[0]

    # Fetch org products and validate subscription status
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'PENDING_STAFF_REVIEW',
                                             qsln_product_info['subscriptions'][0]['productCode'],
                                             'PENDING_STAFF_REVIEW')

    # Should show up as a review task for staff
    rv = client.get('/api/v1/tasks', headers=staff_headers, content_type='application/json')

    item_list = rv.json
    assert schema_utils.validate(item_list, 'paged_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK
    assert len(item_list['tasks']) == 1

    task = item_list['tasks'][0]
    assert task['relationshipStatus'] == 'PENDING_STAFF_REVIEW'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == qsln_product_info['subscriptions'][0]['externalSourceId']

    # Approve task
    rv = client.put('/api/v1/tasks/{}'.format(task['id']),
                    data=json.dumps({'relationshipStatus': 'ACTIVE'}),
                    headers=staff_headers, content_type='application/json')

    task = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert task['relationshipStatus'] == 'ACTIVE'
    assert task['relationshipType'] == 'PRODUCT'
    assert task['action'] == 'QUALIFIED_SUPPLIER_REVIEW'
    assert task['externalSourceId'] == qsln_product_info['subscriptions'][0]['externalSourceId']

    # MHR parent and sub product should be approved
    assert_product_parent_and_child_statuses(client, jwt,
                                             dictionary.get('id'),
                                             'MHR', 'ACTIVE',
                                             qsln_product_info['subscriptions'][0]['productCode'], 'ACTIVE')

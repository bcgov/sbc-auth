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

from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo, TestOrgProductsInfo
from tests.utilities.factory_utils import factory_auth_header

from auth_api.schemas import utils as schema_utils
from auth_api import status as http_status


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

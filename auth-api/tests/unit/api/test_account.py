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

"""Tests to verify the accounts API end-point.

Test-Suite to ensure that the /accounts endpoint is working as expected.
"""

import copy

from auth_api import status as http_status
from tests.utilities.factory_scenarios import TestJwtClaims
from tests.utilities.factory_utils import (
    TestOrgInfo, TestOrgTypeInfo, factory_auth_header, factory_membership_model, factory_org_model,
    factory_product_model, factory_user_model)


def test_authorizations_for_account_returns_200(app, client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for product returns 200."""
    product_code = 'PPR'
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)

    claims = copy.deepcopy(TestJwtClaims.public_user_role.value)
    claims['sub'] = str(user.keycloak_guid)

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f'/api/v1/accounts/{org.id}/products/{product_code}/authorizations',
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert len(rv.json.get('roles')) == 0


def test_authorizations_for_account_with_search_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for product returns 200."""
    product_code = 'PPR'
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id)

    claims = copy.deepcopy(TestJwtClaims.public_user_role.value)
    claims['sub'] = str(user.keycloak_guid)

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f'/api/v1/accounts/{org.id}/products/{product_code}/authorizations',
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('roles') == ['search']


def test_authorizations_with_multiple_accounts_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for product returns 200."""
    product_code = 'PPR'
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id)

    org2 = factory_org_model(org_info=TestOrgInfo.org2, org_type_info=TestOrgTypeInfo.implicit, org_status_info=None,
                             payment_type_info=None)
    factory_membership_model(user.id, org.id)

    claims = copy.deepcopy(TestJwtClaims.public_user_role.value)
    claims['sub'] = str(user.keycloak_guid)

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f'/api/v1/accounts/{org2.id}/products/{product_code}/authorizations',
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert len(rv.json.get('roles')) == 0

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(f'/api/v1/accounts/{org.id}/products/{product_code}/authorizations',
                    headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('roles') == ['search']

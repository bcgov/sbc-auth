# Copyright © 2025 Province of British Columbia
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

Test-Suite to ensure that the /orgs/authorisations endpoint is working as expected.
"""

import json
from http import HTTPStatus

import pytest
from faker import Faker

from auth_api.services.keycloak import KeycloakService
from auth_api.utils.enums import LoginSource
from tests.utilities.factory_scenarios import CONFIG, KeycloakScenario, TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_auth_header

fake = Faker()


def generate_claims_payload(realm_access, login_source):
    """Generate unique claims payload with different names."""
    return {
        "iss": CONFIG.JWT_OIDC_TEST_ISSUER,
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "preferred_username": fake.user_name(),
        "realm_access": realm_access,
        "loginSource": login_source,
    }


def generate_user_headers(jwt, claim, login_source):
    """Create KC User and generate JWT for headers."""
    claims = generate_claims_payload(claim["realm_access"], login_source)
    request = KeycloakScenario.create_user_by_user_info(claims)
    KeycloakService.add_user(request, return_if_exists=True)
    kc_user = KeycloakService.get_user_by_username(request.user_name)
    claims["id"] = kc_user.id
    claims["sub"] = kc_user.id
    return kc_user, factory_auth_header(jwt=jwt, claims=claims)


@pytest.mark.parametrize(
    "test_name,test_data",
    [
        (
            "account_creator",
            {"claim": None, "login_source": None, "get_status": HTTPStatus.OK, "update_status": HTTPStatus.CREATED},
        ),
        (
            "staff",
            {
                "claim": TestJwtClaims.staff_role,
                "login_source": LoginSource.IDIR.value,
                "get_status": HTTPStatus.OK,
                "update_status": HTTPStatus.CREATED,
            },
        ),
        (
            "Forbidden_gov_account",
            {
                "claim": TestJwtClaims.gov_account_holder_user,
                "login_source": LoginSource.IDIR.value,
                "get_status": HTTPStatus.FORBIDDEN,
                "update_status": HTTPStatus.FORBIDDEN,
            },
        ),
        (
            "Forbidden_bceid_account",
            {
                "claim": TestJwtClaims.public_bceid_user,
                "login_source": LoginSource.BCEID.value,
                "get_status": HTTPStatus.FORBIDDEN,
                "update_status": HTTPStatus.FORBIDDEN,
            },
        ),
        (
            "Forbidden_bcsc_account",
            {
                "claim": TestJwtClaims.public_user_role,
                "login_source": LoginSource.BCSC.value,
                "get_status": HTTPStatus.FORBIDDEN,
                "update_status": HTTPStatus.FORBIDDEN,
            },
        ),
    ],
)
def test_org_login_options_permissions(test_name, test_data, client, jwt, session, keycloak_mock):
    """Assert get login options permissions are correct."""
    test_claim = test_data["claim"]
    test_login_source = test_data["login_source"]
    expected_get_status = test_data["get_status"]
    expected_update_status = test_data["update_status"]
    public_user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    _, test_user_headers = (
        generate_user_headers(jwt, test_claim, test_login_source)
        if test_claim is not None
        else (None, public_user_headers)
    )
    client.post("/api/v1/users", headers=public_user_headers, content_type="application/json")
    client.post("/api/v1/users", headers=test_user_headers, content_type="application/json")

    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=public_user_headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    org = json.loads(rv.data)
    org_id = org["id"]

    rv = client.get(f"/api/v1/orgs/{org_id}/login-options", headers=test_user_headers, content_type="application/json")
    assert rv.status_code == expected_get_status

    rv = client.post(
        f"/api/v1/orgs/{org_id}/login-options",
        data=json.dumps({"loginOption": LoginSource.BCSC.value}),
        headers=test_user_headers,
        content_type="application/json",
    )

    assert rv.status_code == expected_update_status

    rv = client.put(
        f"/api/v1/orgs/{org_id}/login-options",
        data=json.dumps({"loginOption": LoginSource.BCEID.value}),
        headers=test_user_headers,
        content_type="application/json",
    )

    assert rv.status_code == expected_update_status

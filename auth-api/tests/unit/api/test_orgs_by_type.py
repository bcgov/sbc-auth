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

"""Tests to verify the org creation process and security group grants by org type.

Test-Suite to ensure that the proper security groups are granted based on org type.
"""

import json
from http import HTTPStatus

import pytest
from faker import Faker

from auth_api.models import Org as OrgModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.constants import GROUP_CONTACT_CENTRE_STAFF, GROUP_MAXIMUS_STAFF, GROUP_SBC_STAFF
from auth_api.utils.enums import LoginSource, OrgType
from auth_api.utils.roles import ADMIN
from tests.utilities.factory_scenarios import CONFIG, KeycloakScenario, TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_auth_header, factory_invitation, keycloak_add_user, keycloak_get_user_by_username

fake = Faker()


def generate_claims_gov_user_payload():
    """Generate unique claims payload with different names."""
    return {
        "iss": CONFIG.JWT_OIDC_TEST_ISSUER,
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "preferred_username": fake.user_name(),
        "realm_access": {"roles": ["public_user", "account_holder", "gov_account_user"]},
        "loginSource": LoginSource.IDIR.value,
    }


def generate_gov_user_headers(jwt):
    """Create KC User and generate JWT for headers."""
    claims = generate_claims_gov_user_payload()
    request = KeycloakScenario.create_user_by_user_info(claims)
    keycloak_add_user(request, return_if_exists=True)
    kc_user = keycloak_get_user_by_username(request.user_name)
    claims["id"] = kc_user.id
    claims["sub"] = kc_user.id
    return kc_user, factory_auth_header(jwt=jwt, claims=claims)


def assert_invite(client, org_id, headers_inviter, headers_invitee, kc_invitee, security_group):
    """Assert invitation send and accept flow."""
    rv = client.post(
        "/api/v1/invitations",
        data=json.dumps(factory_invitation(org_id, "test@email.com", membership_type=ADMIN)),
        headers=headers_inviter,
        content_type="application/json",
    )
    invitation_dict = json.loads(rv.data)
    invitation_token = invitation_dict["token"]

    rv = client.put(
        f"/api/v1/invitations/tokens/{invitation_token}",
        headers=headers_invitee,
        content_type="application/json",
    )

    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    assert dictionary["status"] == "ACCEPTED"

    kc_user_groups = KeycloakService.get_user_groups(kc_invitee.id)
    assert kc_user_groups
    assert any(group["name"] == security_group for group in kc_user_groups)


@pytest.mark.parametrize(
    "security_group, org_type",
    [
        (GROUP_MAXIMUS_STAFF, OrgType.MAXIMUS_STAFF.value),
        (GROUP_CONTACT_CENTRE_STAFF, OrgType.CC_STAFF.value),
        (GROUP_SBC_STAFF, OrgType.SBC_STAFF.value),
    ],
)
def test_keycloak_groups_by_org_type(security_group, org_type, client, jwt, session, disable_org_update_listener):
    """Assert that proper security groups granted by org type."""
    headers_staff_admin = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    kc_gov_admin, headers_gov_account_admin = generate_gov_user_headers(jwt)
    kc_gov_user, headers_gov_account_user = generate_gov_user_headers(jwt)

    client.post("/api/v1/users", headers=headers_gov_account_admin, content_type="application/json")
    client.post("/api/v1/users", headers=headers_gov_account_user, content_type="application/json")
    client.post("/api/v1/users", headers=headers_staff_admin, content_type="application/json")

    rv = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.org_govm),
        headers=headers_staff_admin,
        content_type="application/json",
    )
    dictionary = json.loads(rv.data)
    assert dictionary.get("branchName") == TestOrgInfo.org_govm.get("branchName")
    org_id = dictionary["id"]
    org_type_model = OrgTypeModel.get_type_for_code(org_type)
    org = OrgModel.find_by_org_id(org_id)
    org.org_type = org_type_model  # Requires the disable_org_update_listener fixture to bypass type_code change check
    org.save()

    # Confirm account create admin invitation flow and added security group - staff user inviting
    assert_invite(client, org_id, headers_staff_admin, headers_gov_account_admin, kc_gov_admin, security_group)

    # Confirm admin inviting member flow and added security group - admin user inviting
    assert_invite(client, org_id, headers_gov_account_admin, headers_gov_account_user, kc_gov_user, security_group)

    rv = client.get(f"/api/v1/orgs/{org_id}/members?status=ACTIVE", headers=headers_staff_admin)
    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    members = dictionary["members"]
    assert dictionary["members"]
    assert len(members) == 2

    # Confirm deactivating membership also removed security group
    rv = client.patch(
        "/api/v1/orgs/{}/members/{}".format(org_id, members[1]["id"]),
        headers=headers_gov_account_admin,
        data=json.dumps({"status": "INACTIVE"}),
        content_type="application/json",
    )

    rv = client.get(f"/api/v1/orgs/{org_id}/members?status=ACTIVE", headers=headers_staff_admin)
    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    members = dictionary["members"]
    assert dictionary["members"]
    assert len(members) == 1

    gov_user_groups = KeycloakService.get_user_groups(kc_gov_user.id)
    assert gov_user_groups
    assert not any(group["name"] == security_group for group in gov_user_groups)

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

"""Tests to assure the permissions API end-point.

Test-Suite to ensure that the /permissions endpoint is working as expected.
"""

import json
from http import HTTPStatus

import pytest

from auth_api.models import OrgType as OrgTypeModel
from auth_api.utils.enums import OrgType
from tests.utilities.factory_scenarios import TestJwtClaims, TestUserInfo
from tests.utilities.factory_utils import (
    factory_auth_header,
    factory_membership_model,
    factory_org_model,
    factory_user_model,
)


def test_permissions_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert get permissions endpoint returns 200."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get("/api/v1/permissions/active/admin?case=upper", headers=headers, content_type="application/json")

    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    present = "CHANGE_ORG_NAME" in dictionary
    assert present is True

    """Assert get permissions endpoint returns 200."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get("/api/v1/permissions/foo/bar", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    assert len(dictionary) == 0


def test_returns_empty_string_permissions(client, jwt, session):  # pylint:disable=unused-argument
    """Assert get permissions endpoint returns 200."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get("/api/v1/permissions/active/admin?case=upper", headers=headers, content_type="application/json")

    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    present = "VIEW_USER_LOGINSOURCE" in dictionary
    assert present is True


@pytest.mark.parametrize(
    "org_type, claims, expected",
    [
        (OrgType.MAXIMUS_STAFF.value, TestJwtClaims.external_staff_readonly_role, True),
        (OrgType.CC_STAFF.value, TestJwtClaims.external_staff_readonly_role, True),
        (OrgType.SBC_FIN_STAFF.value, TestJwtClaims.sbc_finance_staff_role, True),
        (OrgType.MAXIMUS_STAFF.value, TestJwtClaims.public_user_role, False),
        (OrgType.SBC_FIN_STAFF.value, TestJwtClaims.public_user_role, False),
    ],
)
def test_permissions_include_org_type_permissions(
    client, jwt, session, disable_org_update_listener, org_type, claims, expected
):
    """Assert org type permissions are added only for read-only staff roles."""
    user = factory_user_model(
        user_info={**TestUserInfo.user1, "keycloak_guid": claims["sub"], "idp_userid": claims["idp_userid"]}
    )
    org = factory_org_model(user_id=user.id)
    org.org_type = OrgTypeModel.get_type_for_code(org_type)
    org.save()
    factory_membership_model(user.id, org.id, member_type="USER")

    headers = factory_auth_header(jwt=jwt, claims=claims)
    rv = client.get(
        "/api/v1/permissions/active/user?includeAllPermissions=true", headers=headers, content_type="application/json"
    )

    assert rv.status_code == HTTPStatus.OK
    assert ("view_launch_titles" in json.loads(rv.data)) is expected

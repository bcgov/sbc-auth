# Copyright © 2026 Province of British Columbia
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
"""Tests to verify the org redirect-url endpoints."""

import copy
import json
from http import HTTPStatus

from tests.utilities.factory_scenarios import TestJwtClaims, TestUserInfo
from tests.utilities.factory_utils import (
    factory_auth_header,
    factory_membership_model,
    factory_org_model,
    factory_redirect_url_model,
    factory_user_model,
)


def _account_holder_headers(jwt, user):
    """Return auth headers with account_holder role and the user's keycloak_guid as sub."""
    claims = copy.deepcopy(TestJwtClaims.public_account_holder_user.value)
    claims["sub"] = str(user.keycloak_guid)
    return factory_auth_header(jwt=jwt, claims=claims)


def test_add_redirect_url(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a redirect URL is added for the org."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)

    rv = client.post(
        f"/api/v1/orgs/{org.id}/redirect-urls",
        headers=_account_holder_headers(jwt, user),
        content_type="application/json",
        data=json.dumps({"redirectUrl": "https://vendor.example.com/callback"}),
    )

    assert rv.status_code == HTTPStatus.CREATED
    data = rv.json
    assert data.get("redirectUrl") == "https://vendor.example.com/callback"
    assert data.get("orgId") == org.id
    assert data.get("createdDate")


def test_add_redirect_url_without_url_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that omitting redirectUrl returns 400."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)

    rv = client.post(
        f"/api/v1/orgs/{org.id}/redirect-urls",
        headers=_account_holder_headers(jwt, user),
        content_type="application/json",
        data=json.dumps({}),
    )

    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_add_duplicate_redirect_url_returns_409(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a duplicate redirect URL returns 409."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback")

    rv = client.post(
        f"/api/v1/orgs/{org.id}/redirect-urls",
        headers=_account_holder_headers(jwt, user),
        content_type="application/json",
        data=json.dumps({"redirectUrl": "https://vendor.example.com/callback"}),
    )

    assert rv.status_code == HTTPStatus.CONFLICT


def test_get_redirect_urls(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that all redirect URLs for the org are returned."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/one")
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/two")

    rv = client.get(f"/api/v1/orgs/{org.id}/redirect-urls", headers=_account_holder_headers(jwt, user))

    assert rv.status_code == HTTPStatus.OK
    urls = [record["redirectUrl"] for record in rv.json["redirectUrls"]]
    assert set(urls) == {"https://vendor.example.com/one", "https://vendor.example.com/two"}


def test_update_redirect_url(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a redirect URL can be updated."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    record = factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/old")

    rv = client.patch(
        f"/api/v1/orgs/{org.id}/redirect-urls/{record.id}",
        headers=_account_holder_headers(jwt, user),
        content_type="application/json",
        data=json.dumps({"redirectUrl": "https://vendor.example.com/new"}),
    )

    assert rv.status_code == HTTPStatus.OK
    assert rv.json.get("redirectUrl") == "https://vendor.example.com/new"


def test_update_redirect_url_scoped_to_org(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a redirect URL from another org cannot be updated."""
    user = factory_user_model(TestUserInfo.user1)
    org_a = factory_org_model()
    org_b = factory_org_model()
    factory_membership_model(user.id, org_a.id)
    factory_membership_model(user.id, org_b.id)
    record = factory_redirect_url_model(org_id=org_b.id)

    headers = _account_holder_headers(jwt, user)
    rv = client.patch(
        f"/api/v1/orgs/{org_a.id}/redirect-urls/{record.id}",
        headers=headers,
        content_type="application/json",
        data=json.dumps({"redirectUrl": "https://vendor.example.com/new"}),
    )
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_delete_redirect_url(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a redirect URL can be deleted."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    record = factory_redirect_url_model(org_id=org.id)

    rv = client.delete(f"/api/v1/orgs/{org.id}/redirect-urls/{record.id}", headers=_account_holder_headers(jwt, user))

    assert rv.status_code == HTTPStatus.OK
    assert client.get(f"/api/v1/orgs/{org.id}/redirect-urls", headers=_account_holder_headers(jwt, user)).json[
        "redirectUrls"
    ] == []


def test_add_redirect_url_forbidden_without_role(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user without account_holder role cannot add a redirect URL."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post(f"/api/v1/orgs/{org.id}/redirect-urls", headers=headers)

    assert rv.status_code == HTTPStatus.UNAUTHORIZED

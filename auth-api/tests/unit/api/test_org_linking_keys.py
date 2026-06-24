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
"""Tests to verify the org linking-key endpoints."""

import copy
import json
from http import HTTPStatus

from tests.utilities.factory_scenarios import TestJwtClaims, TestUserInfo
from tests.utilities.factory_utils import (
    factory_auth_header,
    factory_linking_key_model,
    factory_membership_model,
    factory_org_model,
    factory_user_model,
)


def _account_holder_headers(jwt, user):
    """Return auth headers with account_holder role and the user's keycloak_guid as sub."""
    claims = copy.deepcopy(TestJwtClaims.public_account_holder_user.value)
    claims["sub"] = str(user.keycloak_guid)
    return factory_auth_header(jwt=jwt, claims=claims)


def test_generate_linking_key(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a linking key is generated and the key value is returned once."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    vendor = factory_org_model()
    factory_membership_model(user.id, org.id)

    rv = client.post(
        f"/api/v1/orgs/{org.id}/linking-keys",
        headers=_account_holder_headers(jwt, user),
        content_type="application/json",
        data=json.dumps({"vendorAccountId": vendor.id}),
    )

    assert rv.status_code == HTTPStatus.CREATED
    data = rv.json
    assert data.get("linkingKey"), "Key value must be returned on creation"
    assert data.get("accountId") == org.id
    assert data.get("vendorAccountId") == vendor.id
    assert data.get("status") == "ACTIVE"
    assert data.get("expiresOn")
    assert data.get("lastUsed") is None


def test_generate_linking_key_without_vendor_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that omitting vendorAccountId returns 400."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)

    rv = client.post(
        f"/api/v1/orgs/{org.id}/linking-keys",
        headers=_account_holder_headers(jwt, user),
        content_type="application/json",
        data=json.dumps({}),
    )

    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_generate_linking_key_with_vendor(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a linking key can be bound to a vendor account at generation."""
    user = factory_user_model(TestUserInfo.user1)
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_membership_model(user.id, lawfirm.id)

    rv = client.post(
        f"/api/v1/orgs/{lawfirm.id}/linking-keys",
        headers=_account_holder_headers(jwt, user),
        content_type="application/json",
        data=json.dumps({"vendorAccountId": vendor.id}),
    )

    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json.get("vendorAccountId") == vendor.id


def test_generate_multiple_keys_for_different_vendors(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a lawfirm can have one active key per vendor simultaneously."""
    user = factory_user_model(TestUserInfo.user1)
    lawfirm = factory_org_model()
    vendor_a = factory_org_model()
    vendor_b = factory_org_model()
    factory_membership_model(user.id, lawfirm.id)

    headers = _account_holder_headers(jwt, user)
    url = f"/api/v1/orgs/{lawfirm.id}/linking-keys"

    rv_a = client.post(
        url, headers=headers, content_type="application/json", data=json.dumps({"vendorAccountId": vendor_a.id})
    )
    rv_b = client.post(
        url, headers=headers, content_type="application/json", data=json.dumps({"vendorAccountId": vendor_b.id})
    )

    assert rv_a.status_code == HTTPStatus.CREATED
    assert rv_b.status_code == HTTPStatus.CREATED
    assert rv_a.json.get("linkingKey") != rv_b.json.get("linkingKey")
    assert rv_a.json.get("vendorAccountId") == vendor_a.id
    assert rv_b.json.get("vendorAccountId") == vendor_b.id

    rv_list = client.get(url, headers=headers)
    assert rv_list.status_code == HTTPStatus.OK
    assert len(rv_list.json.get("linkingKeys")) == 2


def test_regenerate_key_for_same_vendor_revokes_previous(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that regenerating a key for the same vendor revokes the old one."""
    user = factory_user_model(TestUserInfo.user1)
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_membership_model(user.id, lawfirm.id)

    headers = _account_holder_headers(jwt, user)
    url = f"/api/v1/orgs/{lawfirm.id}/linking-keys"
    payload = json.dumps({"vendorAccountId": vendor.id})

    first = client.post(url, headers=headers, content_type="application/json", data=payload)
    assert first.status_code == HTTPStatus.CREATED

    second = client.post(url, headers=headers, content_type="application/json", data=payload)
    assert second.status_code == HTTPStatus.CREATED
    assert second.json.get("linkingKey") != first.json.get("linkingKey")

    rv_list = client.get(url, headers=headers)
    assert len(rv_list.json.get("linkingKeys")) == 1


def test_get_linking_keys_empty(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that GET returns an empty list when no keys exist."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)

    rv = client.get(f"/api/v1/orgs/{org.id}/linking-keys", headers=_account_holder_headers(jwt, user))

    assert rv.status_code == HTTPStatus.OK
    assert rv.json.get("linkingKeys") == []


def test_get_linking_keys_hides_key_value(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that GET never exposes the raw key value."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_linking_key_model(account_id=org.id)

    rv = client.get(f"/api/v1/orgs/{org.id}/linking-keys", headers=_account_holder_headers(jwt, user))

    assert rv.status_code == HTTPStatus.OK
    keys = rv.json.get("linkingKeys")
    assert len(keys) == 1
    assert "linkingKey" not in keys[0], "Raw key must not be exposed on GET"


def test_revoke_linking_key_by_id(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that DELETE revokes a specific linking key by ID."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    record = factory_linking_key_model(account_id=org.id)

    headers = _account_holder_headers(jwt, user)
    rv = client.delete(f"/api/v1/orgs/{org.id}/linking-keys/{record.id}", headers=headers)
    assert rv.status_code == HTTPStatus.OK

    rv_list = client.get(f"/api/v1/orgs/{org.id}/linking-keys", headers=headers)
    assert rv_list.json.get("linkingKeys") == []


def test_revoke_wrong_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that DELETE returns 404 when the key does not belong to the given org."""
    user = factory_user_model(TestUserInfo.user1)
    org_a = factory_org_model()
    org_b = factory_org_model()
    factory_membership_model(user.id, org_a.id)
    factory_membership_model(user.id, org_b.id)
    record = factory_linking_key_model(account_id=org_b.id)

    headers = _account_holder_headers(jwt, user)
    rv = client.delete(f"/api/v1/orgs/{org_a.id}/linking-keys/{record.id}", headers=headers)
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_generate_linking_key_forbidden_without_role(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a user without account_holder role cannot generate a key."""
    user = factory_user_model(TestUserInfo.user1)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post(f"/api/v1/orgs/{org.id}/linking-keys", headers=headers)

    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_linking_keys_disabled_by_flag(client, jwt, session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that all linking-keys endpoints return 501 when disable-account-linking flag is on."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    headers = _account_holder_headers(jwt, user)

    monkeypatch.setattr("auth_api.resources.v1.org_linking_keys.flags.is_on", lambda *_, **__: True)

    assert client.get(f"/api/v1/orgs/{org.id}/linking-keys", headers=headers).status_code == HTTPStatus.NOT_IMPLEMENTED
    assert client.post(f"/api/v1/orgs/{org.id}/linking-keys", headers=headers).status_code == HTTPStatus.NOT_IMPLEMENTED
    assert client.delete(f"/api/v1/orgs/{org.id}/linking-keys/1", headers=headers).status_code == HTTPStatus.NOT_IMPLEMENTED

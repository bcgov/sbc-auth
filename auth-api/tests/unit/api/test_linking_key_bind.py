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
"""Tests to verify the linking-key bind endpoint."""

import copy
import json
from http import HTTPStatus

from auth_api.utils.enums import LinkingKeyStatus
from tests.utilities.factory_scenarios import TestJwtClaims
from tests.utilities.factory_utils import (
    factory_auth_header,
    factory_linking_key_model,
    factory_org_model,
)

_BIND_URL = "/api/v1/linking-keys/bind"


def _vendor_headers(jwt, vendor_id):
    """Return auth headers with account_holder role and vendor's Account-Id claim."""
    claims = copy.deepcopy(TestJwtClaims.public_account_holder_user.value)
    claims["Account-Id"] = str(vendor_id)
    return factory_auth_header(jwt=jwt, claims=claims)


def test_bind_pending_key(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a vendor can bind a PENDING key, activating it."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    pending_key = factory_linking_key_model(account_id=lawfirm.id, status=LinkingKeyStatus.PENDING.value)

    rv = client.post(
        _BIND_URL,
        headers=_vendor_headers(jwt, vendor.id),
        content_type="application/json",
        data=json.dumps({"linkingKey": pending_key.linking_key}),
    )

    assert rv.status_code == HTTPStatus.OK
    assert rv.json.get("status") == "ACTIVE"
    assert rv.json.get("vendorAccountId") == vendor.id
    assert rv.json.get("accountId") == lawfirm.id
    assert "linkingKey" not in rv.json


def test_bind_already_active_key_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that attempting to bind an already ACTIVE key returns 404."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    active_key = factory_linking_key_model(account_id=lawfirm.id, vendor_account_id=vendor.id)

    rv = client.post(
        _BIND_URL,
        headers=_vendor_headers(jwt, vendor.id),
        content_type="application/json",
        data=json.dumps({"linkingKey": active_key.linking_key}),
    )

    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_bind_nonexistent_key_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a key value that doesn't exist returns 404."""
    vendor = factory_org_model()

    rv = client.post(
        _BIND_URL,
        headers=_vendor_headers(jwt, vendor.id),
        content_type="application/json",
        data=json.dumps({"linkingKey": "no-such-key"}),
    )

    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_bind_missing_fields_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that missing required fields returns 400."""
    vendor = factory_org_model()

    rv = client.post(
        _BIND_URL,
        headers=_vendor_headers(jwt, vendor.id),
        content_type="application/json",
        data=json.dumps({}),
    )

    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_bind_without_account_id_in_token_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a call without Account-Id in the token returns 400."""
    lawfirm = factory_org_model()
    pending_key = factory_linking_key_model(account_id=lawfirm.id, status=LinkingKeyStatus.PENDING.value)
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user.value)

    rv = client.post(
        _BIND_URL,
        headers=headers,
        content_type="application/json",
        data=json.dumps({"linkingKey": pending_key.linking_key}),
    )

    assert rv.status_code == HTTPStatus.BAD_REQUEST

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

"""Tests to verify the api keys endpoint.

Test-Suite to ensure that the /orgs/api-keys endpoint is working as expected.
"""

import json
import random
import uuid
from http import HTTPStatus
from unittest.mock import Mock

import pytest
from requests.exceptions import HTTPError
from sqlalchemy import text

from auth_api.exceptions.errors import Error
from auth_api.models.org_api_terms_acceptance import OrgApiTermsAcceptance as OrgApiTermsAcceptanceModel
from auth_api.utils.enums import DocumentType, PaymentAccountStatus
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_auth_header, factory_document_model, factory_membership_model


def set_random_org_id_sequence(session, org_id):
    """Set the org sequence so the next org created will have the random org_id to avoid keycloak conflicts."""
    session.execute(text(f"SELECT setval('orgs_id_seq', {org_id}, false)"))
    session.commit()


@pytest.fixture
def mock_create_payment_settings(monkeypatch):
    """Mock _create_payment_settings to return successful payment account creation."""

    def mock_func(*_args, **_kwargs):
        return PaymentAccountStatus.CREATED, None

    monkeypatch.setattr("auth_api.services.org.Org._create_payment_settings", mock_func)


def test_create_api_keys(client, jwt, session, keycloak_mock, mock_create_payment_settings, monkeypatch):  # pylint:disable=unused-argument
    """Assert that api keys can be generated."""
    org_id = random.randint(1000, 999999)
    set_random_org_id_sequence(session, org_id)

    # First create an account
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json.get("id") == org_id
    assert not rv.json.get("hasApiAccess")

    call_count = {"count": 0}

    def mock_get_404(*_args, **_kwargs):
        """Mock RestService.get to return 404 for consumer_exists check on first call only."""
        call_count["count"] += 1
        if call_count["count"] == 1:
            error_response = Mock()
            error_response.status_code = 404
            raise HTTPError(response=error_response)
        # For subsequent calls, return successful response with consumer data
        mock_response = Mock()
        mock_response.json.return_value = {
            "consumer": {
                "consumerKey": [
                    {
                        "apiKey": "test-api-key-123",
                        "keyName": "TEST",
                        "keyStatus": "approved",
                        "environment": "dev",
                    }
                ]
            }
        }
        mock_response.raise_for_status = lambda: None
        return mock_response

    monkeypatch.setattr("auth_api.services.rest_service.RestService.get", mock_get_404)

    def mock_post(*_args, **_kwargs):
        """Mock RestService.post for creating consumer and API keys."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "consumer": {
                "consumerKey": [
                    {
                        "apiKey": "test-api-key-123",
                        "keyName": "TEST",
                        "keyStatus": "approved",
                        "environment": "dev",
                    }
                ]
            }
        }
        mock_response.raise_for_status = lambda: None
        return mock_response

    monkeypatch.setattr("auth_api.services.rest_service.RestService.post", mock_post)

    def get_pay_account_mock(_org, _user):
        return {"paymentMethod": "PAD"}

    monkeypatch.setattr("auth_api.services.api_gateway.ApiGateway._get_pay_account", get_pay_account_mock)

    # Create a system token and create an API key for this account.
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.post(
        f"/api/v1/orgs/{org_id}/api-keys",
        headers=headers,
        content_type="application/json",
        data=json.dumps({"apiKeyName": "TEST"}),
    )
    assert rv.json["consumer"]["consumerKey"]

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    assert rv.json.get("hasApiAccess")


def test_list_api_keys(client, jwt, session, keycloak_mock, mock_create_payment_settings, monkeypatch):  # pylint:disable=unused-argument
    """Assert that api keys can be listed."""
    org_id = random.randint(1000, 999999)
    set_random_org_id_sequence(session, org_id)

    # First create an account
    user_header = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
    client.post("/api/v1/users", headers=user_header, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=user_header, content_type="application/json"
    )
    assert rv.json.get("id") == org_id

    # Mock RestService.get to return consumer with API keys
    def mock_get(*_args, **_kwargs):
        mock_response = Mock()
        mock_response.json.return_value = {
            "consumer": {
                "consumerKey": [
                    {
                        "apiKey": "test-api-key-1",
                        "keyName": "TEST",
                        "keyStatus": "approved",
                        "environment": "dev",
                    },
                    {
                        "apiKey": "test-api-key-2",
                        "keyName": "TEST 2",
                        "keyStatus": "approved",
                        "environment": "dev",
                    },
                ]
            }
        }
        mock_response.raise_for_status = lambda: None
        return mock_response

    monkeypatch.setattr("auth_api.services.rest_service.RestService.get", mock_get)

    # Mock RestService.post for creating API keys
    def mock_post(*_args, **_kwargs):
        mock_response = Mock()
        mock_response.json.return_value = {
            "consumer": {
                "consumerKey": [
                    {
                        "apiKey": "test-api-key-1",
                        "keyName": "TEST",
                        "keyStatus": "approved",
                        "environment": "dev",
                    }
                ]
            }
        }
        mock_response.raise_for_status = lambda: None
        return mock_response

    monkeypatch.setattr("auth_api.services.rest_service.RestService.post", mock_post)

    # Create a system token and create an API key for this account.
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.post(
        f"/api/v1/orgs/{org_id}/api-keys",
        headers=headers,
        content_type="application/json",
        data=json.dumps({"environment": "dev", "keyName": "TEST"}),
    )

    rv = client.post(
        f"/api/v1/orgs/{org_id}/api-keys",
        headers=headers,
        content_type="application/json",
        data=json.dumps({"environment": "dev", "keyName": "TEST 2"}),
    )

    rv = client.get(f"/api/v1/orgs/{org_id}/api-keys", headers=headers, content_type="application/json")
    assert rv.json["consumer"]["consumerKey"]

    rv = client.get(f"/api/v1/orgs/{org_id}/api-keys", headers=user_header, content_type="application/json")
    assert rv.json["consumer"]["consumerKey"]


def test_revoke_api_key(client, jwt, session, keycloak_mock, mock_create_payment_settings, monkeypatch):  # pylint:disable=unused-argument
    """Assert that api keys can be revoked."""
    org_id = random.randint(1000, 999999)
    set_random_org_id_sequence(session, org_id)

    # First create an account
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
    rv = client.post("/api/v1/users", headers=user_headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=user_headers, content_type="application/json"
    )
    assert rv.json.get("id") == org_id

    test_api_key = "test-api-key-to-revoke"

    # Mock RestService.get to return consumer with API keys
    def mock_get(*_args, **_kwargs):
        mock_response = Mock()
        mock_response.json.return_value = {
            "consumer": {
                "consumerKey": [
                    {
                        "apiKey": test_api_key,
                        "keyName": "TEST",
                        "keyStatus": "approved",
                        "environment": "dev",
                        "email": f"{org_id}@test.gov.bc.ca",
                    }
                ]
            }
        }
        mock_response.raise_for_status = lambda: None
        return mock_response

    monkeypatch.setattr("auth_api.services.rest_service.RestService.get", mock_get)

    # Mock RestService.post for creating API keys
    def mock_post(*_args, **_kwargs):
        mock_response = Mock()
        mock_response.json.return_value = {
            "consumer": {
                "consumerKey": [
                    {
                        "apiKey": test_api_key,
                        "keyName": "TEST",
                        "keyStatus": "approved",
                        "environment": "dev",
                    }
                ]
            }
        }
        mock_response.raise_for_status = lambda: None
        return mock_response

    monkeypatch.setattr("auth_api.services.rest_service.RestService.post", mock_post)

    # Mock RestService.patch for revoking API keys
    def mock_patch(*_args, **_kwargs):
        assert _kwargs["data"] == {}
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = lambda: None
        return mock_response

    monkeypatch.setattr("auth_api.services.rest_service.RestService.patch", mock_patch)

    # Create a system token and create an API key for this account.
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.post(
        f"/api/v1/orgs/{org_id}/api-keys",
        headers=headers,
        content_type="application/json",
        data=json.dumps({"environment": "dev", "keyName": "TEST"}),
    )

    rv = client.get(f"/api/v1/orgs/{org_id}/api-keys", headers=headers, content_type="application/json")
    key = rv.json["consumer"]["consumerKey"][0]["apiKey"]

    rv = client.delete(f"/api/v1/orgs/{org_id}/api-keys/{key}", headers=headers, content_type="application/json")
    assert rv.status_code == 200

    # Mock get_api_keys to return empty when revoking invalid key
    def mock_get_invalid(*_args, **_kwargs):
        mock_response = Mock()
        mock_response.json.return_value = {"consumer": {"consumerKey": []}}
        mock_response.raise_for_status = lambda: None
        return mock_response

    monkeypatch.setattr("auth_api.services.rest_service.RestService.get", mock_get_invalid)

    # Revoke an invalid key
    rv = client.delete(
        f"/api/v1/orgs/{org_id}/api-keys/{key}-INVALID", headers=user_headers, content_type="application/json"
    )
    assert rv.status_code == 404


_STAFF_SUB = str(uuid.uuid4())


def _create_org_as_account_holder(client, jwt):
    """Create an org through the API; the account holder is its admin."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    return rv.json.get("id"), headers


def _post_terms(client, org_id, headers, payload):
    return client.post(
        f"/api/v1/orgs/{org_id}/api-keys/terms",
        headers=headers,
        content_type="application/json",
        data=json.dumps(payload),
    )


def test_get_and_accept_api_terms(client, jwt, session, keycloak_mock, mock_create_payment_settings):  # pylint:disable=unused-argument
    """Assert that the account holder can read the terms status and accept the terms."""
    org_id, headers = _create_org_as_account_holder(client, jwt)
    claims = TestJwtClaims.public_account_holder_user

    rv = client.get(f"/api/v1/orgs/{org_id}/api-keys/terms", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert rv.json == {"isAccepted": False, "acceptedVersionId": None, "acceptedBy": None, "acceptedOn": None}

    rv = _post_terms(client, org_id, headers, {"versionId": "k01"})
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json["isAccepted"] is True
    assert rv.json["acceptedVersionId"] == "k01"
    assert rv.json["acceptedBy"] == claims["preferred_username"]
    assert rv.json["acceptedOn"]

    rv = client.get(f"/api/v1/orgs/{org_id}/api-keys/terms", headers=headers, content_type="application/json")
    assert rv.json == _post_terms(client, org_id, headers, {"versionId": "k01"}).json


def test_staff_cannot_accept_api_terms(client, jwt, session, keycloak_mock, mock_create_payment_settings):  # pylint:disable=unused-argument
    """Assert that staff can read the terms status but cannot accept the terms on the account's behalf."""
    org_id, _ = _create_org_as_account_holder(client, jwt)
    # the scenario's staff claims share the account holder's sub, so use a separate staff user
    staff_claims = {**TestJwtClaims.staff_manage_accounts_role, "sub": _STAFF_SUB, "idp_userid": _STAFF_SUB}
    headers = factory_auth_header(jwt=jwt, claims=staff_claims)
    client.post("/api/v1/users", headers=headers, content_type="application/json")

    rv = client.get(f"/api/v1/orgs/{org_id}/api-keys/terms", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK

    rv = _post_terms(client, org_id, headers, {"versionId": "k01"})
    assert rv.status_code == HTTPStatus.UNAUTHORIZED
    assert OrgApiTermsAcceptanceModel.find_latest_by_org(org_id) is None


@pytest.mark.parametrize(
    "payload",
    [{}, {"versionId": ""}, {"versionId": 1}, {"versionId": "k01", "other": "value"}],
    ids=["missing", "empty", "not_a_string", "extra_property"],
)
def test_accept_api_terms_invalid_payload(client, jwt, session, keycloak_mock, mock_create_payment_settings, payload):  # pylint:disable=unused-argument
    """Assert that a request that doesn't match the acceptance schema is rejected."""
    org_id, headers = _create_org_as_account_holder(client, jwt)

    rv = _post_terms(client, org_id, headers, payload)

    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_accept_api_terms_version_mismatch(client, jwt, session, keycloak_mock, mock_create_payment_settings):  # pylint:disable=unused-argument
    """Assert that accepting a version that isn't the latest is rejected with its error code."""
    org_id, headers = _create_org_as_account_holder(client, jwt)
    factory_document_model("k02", DocumentType.TERMS_OF_USE_API.value, "<p>Updated terms</p>")

    rv = _post_terms(client, org_id, headers, {"versionId": "k01"})

    assert rv.status_code == HTTPStatus.BAD_REQUEST
    assert rv.json["code"] == Error.API_TERMS_VERSION_MISMATCH.name


@pytest.mark.parametrize("member_type", ["USER", "COORDINATOR"])
def test_api_terms_forbidden_for_non_admin_member(
    client, jwt, session, keycloak_mock, mock_create_payment_settings, member_type
):  # pylint:disable=unused-argument
    """Assert that a member who isn't an admin of the account gets a 403 reading or accepting the terms."""
    org_id, _ = _create_org_as_account_holder(client, jwt)
    # an account holder of some other account, who is only a member of this one
    member_claims = TestJwtClaims.get_test_real_user(uuid.uuid4(), roles=["account_holder"])
    member_headers = factory_auth_header(jwt=jwt, claims=member_claims)
    rv = client.post("/api/v1/users", headers=member_headers, content_type="application/json")
    factory_membership_model(rv.json["id"], org_id, member_type=member_type)

    rv = client.get(f"/api/v1/orgs/{org_id}/api-keys/terms", headers=member_headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.FORBIDDEN

    rv = _post_terms(client, org_id, member_headers, {"versionId": "k01"})
    assert rv.status_code == HTTPStatus.FORBIDDEN
    assert OrgApiTermsAcceptanceModel.find_latest_by_org(org_id) is None


def test_create_api_key_requires_terms_acceptance(client, jwt, session, keycloak_mock, mock_create_payment_settings):  # pylint:disable=unused-argument
    """Assert that creating a key before the latest terms are accepted is rejected with its error code."""
    org_id, headers = _create_org_as_account_holder(client, jwt)

    rv = client.post(
        f"/api/v1/orgs/{org_id}/api-keys",
        headers=headers,
        content_type="application/json",
        data=json.dumps({"keyName": "TEST"}),
    )

    assert rv.status_code == HTTPStatus.BAD_REQUEST
    assert rv.json["code"] == Error.API_TERMS_NOT_ACCEPTED.name


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="no_name"),
        pytest.param({"apiKeyName": ""}, id="empty_name"),
        pytest.param({"apiKeyName": " TEST"}, id="leading_whitespace"),
    ],
)
def test_create_api_key_invalid_payload(client, jwt, session, keycloak_mock, mock_create_payment_settings, payload):  # pylint:disable=unused-argument
    """Assert that a create key payload without a valid key name is rejected by the schema."""
    org_id, headers = _create_org_as_account_holder(client, jwt)

    rv = client.post(
        f"/api/v1/orgs/{org_id}/api-keys",
        headers=headers,
        content_type="application/json",
        data=json.dumps(payload),
    )

    assert rv.status_code == HTTPStatus.BAD_REQUEST
    # schema errors have no code, unlike the terms check which also returns 400
    assert "code" not in rv.json

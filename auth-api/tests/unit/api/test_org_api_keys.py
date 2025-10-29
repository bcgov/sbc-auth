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
from http import HTTPStatus
from unittest.mock import Mock

import pytest
from requests.exceptions import HTTPError
from sqlalchemy import text

from auth_api.utils.enums import PaymentAccountStatus
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_auth_header


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
        data=json.dumps({"keyName": "TEST"}),
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

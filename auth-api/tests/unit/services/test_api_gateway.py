"""Test module for API Gateway service."""

import os
from unittest.mock import Mock

import pytest
from flask import current_app

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.org_api_terms_acceptance import OrgApiTermsAcceptance as OrgApiTermsAcceptanceModel
from auth_api.services.api_gateway import ApiGateway
from auth_api.services.keycloak import KeycloakService
from auth_api.services.rest_service import RestService
from auth_api.utils.constants import MAX_NAMED_API_KEYS
from auth_api.utils.enums import DocumentType
from tests.utilities.factory_scenarios import TestUserInfo
from tests.utilities.factory_utils import (
    factory_document_model,
    factory_membership_model,
    factory_org_model,
    factory_user_model,
    patch_token_info,
)


@pytest.mark.skip(reason="ADHOC Test for API users creation and Gateway")
def test_keycloak_test_environment():
    """Adhoc test with test secrets that can be run to test the functionality of the api gateway code."""
    current_app.config["KEYCLOAK_BASE_URL"] = os.getenv("KEYCLOAK_BASE_URL")
    current_app.config["KEYCLOAK_REALMNAME"] = os.getenv("KEYCLOAK_REALMNAME")
    current_app.config["KEYCLOAK_ADMIN_USERNAME"] = os.getenv("SBC_AUTH_ADMIN_CLIENT_ID")
    current_app.config["KEYCLOAK_ADMIN_SECRET"] = os.getenv("SBC_AUTH_ADMIN_CLIENT_SECRET")
    current_app.config["API_GW_KC_CLIENT_ID_PATTERN"] = os.getenv("API_GW_KC_CLIENT_ID_PATTERN")
    KeycloakService.get_service_account_by_client_name(ApiGateway.get_api_client_id(2758, "sandbox"))
    ApiGateway._create_user_and_membership_for_api_user(2758, "sandbox")
    assert True


def _setup_create_key(monkeypatch, claims_roles, member_type=None):
    """Create an org and a user with the given realm roles and optional membership, and mock the gateway calls."""
    user = factory_user_model(TestUserInfo.user_test)
    org = factory_org_model()
    if member_type:
        factory_membership_model(user.id, org.id, member_type=member_type)
    patch_token_info(
        {"sub": user.keycloak_guid, "idp_userid": user.idp_userid, "realm_access": {"roles": claims_roles}},
        monkeypatch,
    )

    # the org already has a consumer (the gateway get below succeeds), so a key is added without creating keycloak clients
    monkeypatch.setattr(ApiGateway, "_create_user_and_membership_for_api_user", lambda *_args: None)
    gateway_post = Mock()
    gateway_post.return_value.json.return_value = {
        "consumer": {"consumerKey": [{"apiKey": "new-api-key", "apiKeyName": "TEST", "keyStatus": "approved"}]}
    }
    monkeypatch.setattr("auth_api.services.api_gateway.RestService.post", gateway_post)
    # the consumer's keys are listed once, for the consumer check and the named key limit, the org has none yet
    gateway_get = Mock()
    gateway_get.return_value.json.return_value = {"consumer": {"consumerKey": []}}
    monkeypatch.setattr("auth_api.services.api_gateway.RestService.get", gateway_get)
    return org, gateway_post


@pytest.mark.parametrize(
    "claims_roles, member_type",
    [
        (["public_user", "account_holder"], "ADMIN"),
        (["staff", "view_accounts", "manage_accounts"], None),
    ],
    ids=["account_holder", "staff"],
)
def test_create_key_requires_terms_acceptance(session, monkeypatch, claims_roles, member_type):  # pylint:disable=unused-argument
    """Assert that account holders and staff can only create a key once the latest API terms are accepted."""
    document = factory_document_model("k01", DocumentType.TERMS_OF_USE_API.value, "<p>Terms</p>")
    org, gateway_post = _setup_create_key(monkeypatch, claims_roles, member_type)

    with pytest.raises(BusinessException) as exc_info:
        ApiGateway.create_key(org.id, {"keyName": "TEST"})
    assert exc_info.value.code == Error.API_TERMS_NOT_ACCEPTED.name
    gateway_post.assert_not_called()

    # acceptance is admin-only, so record it directly to cover the staff case too
    OrgApiTermsAcceptanceModel(org_id=org.id, version_id=document.version_id).save()
    response = ApiGateway.create_key(org.id, {"keyName": "TEST"})

    gateway_post.assert_called_once()
    assert [key["apiKey"] for key in response["consumer"]["consumerKey"]] == ["new-api-key"]


def test_create_key_no_terms_document(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that no key can be created when there is no API terms document."""
    org, gateway_post = _setup_create_key(monkeypatch, ["public_user", "account_holder"], "ADMIN")

    with pytest.raises(BusinessException) as exc_info:
        ApiGateway.create_key(org.id, {"keyName": "TEST"})

    assert exc_info.value.code == Error.API_TERMS_NOT_FOUND.name
    gateway_post.assert_not_called()


@pytest.mark.parametrize(
    "include_all, expected_keys",
    [(False, ["approved-key"]), (True, ["approved-key", "revoked-key"])],
    ids=["default_approved_only", "all_includes_revoked"],
)
def test_get_api_keys_status_filter(monkeypatch, include_all, expected_keys):
    """Assert revoked keys are only returned when include_all is set."""
    gateway_get = Mock()
    gateway_get.return_value.json.return_value = {
        "consumer": {
            "consumerKey": [
                {"apiKey": "approved-key", "keyStatus": "approved"},
                {"apiKey": "revoked-key", "keyStatus": "revoked"},
            ]
        }
    }
    monkeypatch.setattr("auth_api.services.api_gateway.RestService.get", gateway_get)

    response = ApiGateway.get_api_keys(1, skip_auth=True, include_all=include_all)

    assert [key["apiKey"] for key in response["consumer"]["consumerKey"]] == expected_keys


@pytest.mark.parametrize("payload, get_count", [({"apiKeyName": "TEST"}, 2), ({}, 1)], ids=["named", "unnamed"])
def test_create_key_gateway_lookups(session, monkeypatch, payload, get_count):  # pylint:disable=unused-argument
    """Assert only a named create lists the consumer's keys, to check the named key limit."""
    document = factory_document_model("k01", DocumentType.TERMS_OF_USE_API.value, "<p>Terms</p>")
    org, gateway_post = _setup_create_key(monkeypatch, ["public_user", "account_holder"], "ADMIN")
    OrgApiTermsAcceptanceModel(org_id=org.id, version_id=document.version_id).save()

    ApiGateway.create_key(org.id, payload)

    gateway_post.assert_called_once()
    assert RestService.get.call_count == get_count


def test_create_key_named_limit_reached(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert a named key isn't created once the org has the maximum number of named keys."""
    document = factory_document_model("k01", DocumentType.TERMS_OF_USE_API.value, "<p>Terms</p>")
    org, gateway_post = _setup_create_key(monkeypatch, ["public_user", "account_holder"], "ADMIN")
    OrgApiTermsAcceptanceModel(org_id=org.id, version_id=document.version_id).save()
    gateway_get = Mock()
    gateway_get.return_value.json.return_value = {
        "consumer": {
            "consumerKey": [
                {"apiKey": f"key-{i}", "apiKeyName": f"Key {i}", "keyStatus": "revoked"}
                for i in range(MAX_NAMED_API_KEYS)
            ]
        }
    }
    monkeypatch.setattr("auth_api.services.api_gateway.RestService.get", gateway_get)

    with pytest.raises(BusinessException) as exc_info:
        ApiGateway.create_key(org.id, {"apiKeyName": "Eleventh"})

    assert exc_info.value.code == Error.API_KEY_NAMED_LIMIT_REACHED.name
    gateway_post.assert_not_called()

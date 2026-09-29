"""Test module for API Gateway service."""

import os
from unittest.mock import Mock

import pytest
from flask import current_app

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.documents import Documents as DocumentsModel
from auth_api.models.org_api_terms_acceptance import OrgApiTermsAcceptance as OrgApiTermsAcceptanceModel
from auth_api.services.api_gateway import ApiGateway
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.enums import DocumentType
from tests.utilities.factory_scenarios import TestUserInfo
from tests.utilities.factory_utils import (
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

    # the org already has a consumer, so a key is added without creating keycloak clients
    monkeypatch.setattr(ApiGateway, "_consumer_exists", lambda *_args: True)
    monkeypatch.setattr(ApiGateway, "_create_user_and_membership_for_api_user", lambda *_args: None)
    gateway_post = Mock()
    gateway_post.return_value.json.return_value = {
        "consumer": {"consumerKey": [{"apiKey": "new-api-key", "apiKeyName": "TEST", "keyStatus": "approved"}]}
    }
    monkeypatch.setattr("auth_api.services.api_gateway.RestService.post", gateway_post)
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
    org, gateway_post = _setup_create_key(monkeypatch, claims_roles, member_type)

    with pytest.raises(BusinessException) as exc_info:
        ApiGateway.create_key(org.id, {"keyName": "TEST"})
    assert exc_info.value.code == Error.API_TERMS_NOT_ACCEPTED.name
    gateway_post.assert_not_called()

    # acceptance is admin-only, so record it directly to cover the staff case too
    latest = DocumentsModel.find_latest_version_by_type(DocumentType.TERMS_OF_USE_API.value)
    OrgApiTermsAcceptanceModel(org_id=org.id, version_id=latest).save()
    response = ApiGateway.create_key(org.id, {"keyName": "TEST"})

    gateway_post.assert_called_once()
    assert [key["apiKey"] for key in response["consumer"]["consumerKey"]] == ["new-api-key"]


def test_create_key_no_terms_document(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that no key can be created when there is no API terms document."""
    org, gateway_post = _setup_create_key(monkeypatch, ["public_user", "account_holder"], "ADMIN")
    DocumentsModel.query.filter_by(type=DocumentType.TERMS_OF_USE_API.value).delete()

    with pytest.raises(BusinessException) as exc_info:
        ApiGateway.create_key(org.id, {"keyName": "TEST"})

    assert exc_info.value.code == Error.API_TERMS_NOT_FOUND.name
    gateway_post.assert_not_called()

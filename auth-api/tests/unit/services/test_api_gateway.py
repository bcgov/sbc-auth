import os

import pytest
from flask import current_app

from auth_api.services.api_gateway import ApiGateway
from auth_api.services.keycloak import KeycloakService


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

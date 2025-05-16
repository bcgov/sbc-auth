# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module manages API gateway service integrations."""

import re
from typing import Dict, List

from flask import current_app
from requests.exceptions import HTTPError
from structured_logging import StructuredLogging

from auth_api.exceptions import BusinessException, Error
from auth_api.models.membership import Membership as MembershipModel
from auth_api.models.org import Org as OrgModel
from auth_api.models.user import User as UserModel
from auth_api.services.authorization import check_auth
from auth_api.services.flags import flags
from auth_api.services.keycloak import KeycloakService
from auth_api.services.membership import Membership as MembershipService
from auth_api.services.rest_service import RestService
from auth_api.utils.api_gateway import generate_client_representation
from auth_api.utils.constants import GROUP_ACCOUNT_HOLDERS, GROUP_API_GW_SANDBOX_USERS, GROUP_API_GW_USERS
from auth_api.utils.enums import Status
from auth_api.utils.roles import ADMIN, STAFF
from auth_api.utils.user_context import UserContext, user_context

logger = StructuredLogging.get_logger()


class ApiGateway:
    """Manages all aspects of the API gateway integration."""

    @classmethod
    def create_key(cls, org_id: int, request_json: Dict[str, str]):
        """Create a key for the account.

        Steps:
        A - If consumer doesn't exist,
        1 - Create a consumer for PROD and one for SANDBOX
        2 - Keycloak Client created for Sandbox consumer added to sandbox group (new role for sandbox)
        3 - Keycloak client created for PROD consumer added to prod group
        B - If consumer already exists,
        1 - Create key for specific environment.
        """
        logger.debug("<create_key ")
        env = current_app.config.get("ENVIRONMENT_NAME")
        name = request_json.get("keyName")
        org: OrgModel = OrgModel.find_by_id(org_id)
        # first find if there is a consumer created for this account.
        consumer_endpoint: str = current_app.config.get("API_GW_CONSUMERS_API_URL")
        gw_api_key = current_app.config.get("API_GW_KEY")
        email = cls._get_email_id(org_id, env)
        if not cls._consumer_exists(email):  # If the account doesn't have api access, add it
            cls._create_consumer(name, org, env=env)
            org.has_api_access = True
            org.save()
            response = cls.get_api_keys(org_id)
        else:
            # Create additional API Key if a consumer exists
            api_key_response = RestService.post(
                f"{consumer_endpoint}/mc/v1/consumers/{email}/apikeys",
                additional_headers={"x-apikey": gw_api_key},
                data={"apiAccess": ["ALL_API"], "apiKeyName": name},
                generate_token=False,
            )
            response = api_key_response.json()

        cls._create_user_and_membership_for_api_user(org_id, env)
        return response

    @classmethod
    def _create_user_and_membership_for_api_user(cls, org_id: int, env: str):
        """Create a user and membership for the api user."""
        client_name = ApiGateway.get_api_client_id(org_id, env)
        client = KeycloakService.get_service_account_by_client_name(client_name)
        if (api_user := UserModel.find_by_username(client_name)) is None:
            api_user = UserModel.create_user_for_api_user(client_name, client.get("id"))
        if MembershipModel.find_membership_by_user_and_org(api_user.id, org_id) is None:
            MembershipService.create_admin_membership_for_api_user(org_id, api_user.id)

    @staticmethod
    def get_api_client_id(org_id, env):
        """Get the client id for the org."""
        client_id_pattern = current_app.config.get("API_GW_KC_CLIENT_ID_PATTERN")
        suffix = "-sandbox" if env != "production" else ""
        client_id = f"{client_id_pattern}{suffix}".format(account_id=org_id)
        return client_id

    @classmethod
    def _create_consumer(cls, name, org, env):
        """Create an API Gateway consumer."""
        consumer_endpoint: str = current_app.config.get("API_GW_CONSUMERS_API_URL")
        gw_api_key = current_app.config.get("API_GW_KEY")
        email = cls._get_email_id(org.id, env)
        client_rep = generate_client_representation(org.id, ApiGateway.get_api_client_id(org.id, env))
        KeycloakService.create_client(client_rep)
        service_account = KeycloakService.get_service_account_user(client_rep.get("id"))

        KeycloakService.add_user_to_group(
            service_account.get("id"), GROUP_API_GW_USERS if env == "production" else GROUP_API_GW_SANDBOX_USERS
        )
        KeycloakService.add_user_to_group(service_account.get("id"), GROUP_ACCOUNT_HOLDERS)
        org_name = cls._make_string_compatible(org.name)
        branch_name = cls._make_string_compatible(org.branch_name or "BCR")
        name = cls._make_string_compatible(name)
        # Create a consumer with the keycloak client id and secret
        create_consumer_payload = {
            "email": email,
            "firstName": org_name,
            "lastName": branch_name,
            "userName": org_name,
            "clientId": client_rep.get("clientId"),
            "clientSecret": client_rep.get("secret"),
            "apiAccess": ["ALL_API"],
            "apiKeyName": name,
        }
        api_key_response = RestService.post(
            f"{consumer_endpoint}/mc/v1/consumers",
            additional_headers={"x-apikey": gw_api_key},
            data=create_consumer_payload,
            generate_token=False,
        )
        return api_key_response

    @classmethod
    def revoke_key(cls, org_id: int, api_key: str):
        """Revoke api key."""
        logger.debug("<revoke_key ")
        check_auth(one_of_roles=(ADMIN, STAFF), org_id=org_id)
        # Find the environment for this key, based on it consumer changes.
        email_id: str = None
        for key in cls.get_api_keys(org_id)["consumer"]["consumerKey"]:
            if key["apiKey"] == api_key:
                email_id = key["email"]
                break
        if not email_id:
            raise BusinessException(Error.DATA_NOT_FOUND, Exception())
        consumer_endpoint = current_app.config.get("API_GW_CONSUMERS_API_URL")
        gw_api_key = current_app.config.get("API_GW_KEY")

        RestService.patch(
            f"{consumer_endpoint}/mc/v1/consumers/{email_id}/apikeys/{api_key}?action=revoke",
            additional_headers={"x-apikey": gw_api_key},
            data={"apiAccess": "ALL_API"},
            generate_token=False,
        )

    @classmethod
    def get_api_keys(cls, org_id: int) -> List[Dict[str, any]]:
        """Get all api keys."""
        logger.debug("<get_api_keys ")
        check_auth(one_of_roles=(ADMIN, STAFF), org_id=org_id)
        api_keys_response = {"consumer": {"consumerKey": []}}
        env = current_app.config.get("ENVIRONMENT_NAME")
        email = cls._get_email_id(org_id, env)
        consumer_endpoint: str = current_app.config.get("API_GW_CONSUMERS_API_URL")
        gw_api_key: str = current_app.config.get("API_GW_KEY")
        try:
            consumers_response = RestService.get(
                f"{consumer_endpoint}/mc/v1/consumers/{email}",
                additional_headers={"x-apikey": gw_api_key},
                skip_404_logging=True,
            )
            keys = consumers_response.json()["consumer"]["consumerKey"]
            cls._filter_and_add_keys(api_keys_response, keys, email)
        except HTTPError as exc:
            if exc.response.status_code != 404:  # If consumer doesn't exist
                raise exc

        return api_keys_response

    @classmethod
    def _filter_and_add_keys(cls, api_keys_response, keys, email):
        def _add_key_to_response(_key):
            if _key["keyStatus"] == "approved":
                _key["email"] = email
                _key["environment"] = "prod" if _key["environment"] == "prod" else "sandbox"
                api_keys_response["consumer"]["consumerKey"].append(_key)

        if isinstance(keys, dict):
            _add_key_to_response(keys)
        elif isinstance(keys, list):
            for key in keys:
                _add_key_to_response(key)

    @classmethod
    def _get_email_id(cls, org_id, env) -> str:
        """Get the email id for the org."""
        if current_app.config.get("API_GW_CONSUMER_EMAIL", None) is not None:
            return current_app.config.get("API_GW_CONSUMER_EMAIL")

        api_gw_email_suffix: str = current_app.config.get("API_GW_EMAIL_SUFFIX")
        id_suffix = "" if env == "production" else "-sandbox"
        email_id = f"{org_id}{id_suffix}@{api_gw_email_suffix}"
        return email_id

    @classmethod
    def _consumer_exists(cls, email):
        """Return if customer exists with this email."""
        consumer_endpoint: str = current_app.config.get("API_GW_CONSUMERS_API_URL")
        gw_api_key: str = current_app.config.get("API_GW_KEY")
        try:
            RestService.get(
                f"{consumer_endpoint}/mc/v1/consumers/{email}",
                additional_headers={"x-apikey": gw_api_key},
                skip_404_logging=True,
            )
        except HTTPError as exc:
            if exc.response.status_code == 404:  # If consumer doesn't exist
                return False
            raise exc

        return True

    @classmethod
    def _get_pay_account(cls, org, user):
        """Get the payment account for the org."""
        pay_accounts_endpoint = f"{current_app.config.get('PAY_API_URL')}/accounts/{org.id}"
        pay_account = RestService.get(endpoint=pay_accounts_endpoint, token=user.bearer_token).json()
        return pay_account

    @classmethod
    def _make_string_compatible(cls, target: str) -> str:
        """Make string compatible for API gateway."""
        # Length 64 max - alphanumeric, space, and the following: . _ -
        target = re.sub(r"[^a-zA-Z0-9_\- .]", "", target)
        return target[:64]

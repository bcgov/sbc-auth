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

from typing import Dict, List

from flask import current_app
from requests.exceptions import HTTPError

from auth_api.exceptions import BusinessException, Error
from auth_api.models.org import Org as OrgModel
from auth_api.services.authorization import check_auth
from auth_api.services.keycloak import KeycloakService
from auth_api.services.rest_service import RestService
from auth_api.utils.api_gateway import generate_client_representation
from auth_api.utils.constants import GROUP_ACCOUNT_HOLDERS, GROUP_API_GW_SANDBOX_USERS, GROUP_API_GW_USERS
from auth_api.utils.roles import ADMIN, STAFF


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
        current_app.logger.debug('<create_key ')
        env = request_json.get('environment', 'sandbox')
        name = request_json.get('keyName')
        org: OrgModel = OrgModel.find_by_id(org_id)
        # first find if there is a consumer created for this account.
        consumer_endpoint: str = current_app.config.get('API_GW_CONSUMERS_API_URL')
        gw_api_key = ApiGateway._get_api_gw_key(env)
        email = cls._get_email_id(org_id, env)
        if not cls._consumer_exists(email):  # If the account doesn't have api access, add it
            cls._create_consumer(name, org, env=env)
            org.has_api_access = True
            org.save()
            response = cls.get_api_keys(org_id)
        else:
            # Create additional API Key if a consumer exists
            api_key_response = RestService.post(
                f'{consumer_endpoint}/mc/v1/consumers/{email}/apikeys',
                additional_headers={'x-apikey': gw_api_key},
                data=dict(
                    apiAccess=['ALL_API'],
                    apiKeyName=name
                ),
                generate_token=False
            )
            response = api_key_response.json()

        return response

    @classmethod
    def _get_api_gw_key(cls, env):
        return current_app.config.get('API_GW_KEY') if env == 'prod' else current_app.config.get(
            'API_GW_NON_PROD_KEY')

    @classmethod
    def _create_consumer(cls, name, org, env):
        """Create an API Gateway consumer."""
        consumer_endpoint: str = current_app.config.get('API_GW_CONSUMERS_API_URL')
        gw_api_key = cls._get_api_gw_key(env)
        email = cls._get_email_id(org.id, env)
        client_rep = generate_client_representation(org.id, current_app.config.get('API_GW_KC_CLIENT_ID_PATTERN'), env)
        KeycloakService.create_client(client_rep)
        service_account = KeycloakService.get_service_account_user(client_rep.get('id'))

        KeycloakService.add_user_to_group(service_account.get('id'),
                                          GROUP_API_GW_USERS if env == 'prod' else GROUP_API_GW_SANDBOX_USERS)
        KeycloakService.add_user_to_group(service_account.get('id'), GROUP_ACCOUNT_HOLDERS)
        # Create a consumer with the keycloak client id and secret
        create_consumer_payload = dict(email=email,
                                       firstName=org.name,
                                       lastName=org.branch_name or 'BCR',
                                       userName=org.name,
                                       clientId=client_rep.get('clientId'),
                                       clientSecret=client_rep.get('secret'),
                                       apiAccess=['ALL_API'],
                                       apiKeyName=name)
        api_key_response = RestService.post(
            f'{consumer_endpoint}/mc/v1/consumers',
            additional_headers={'x-apikey': gw_api_key},
            data=create_consumer_payload,
            generate_token=False
        )
        return api_key_response

    @classmethod
    def revoke_key(cls, org_id: int, api_key: str):
        """Revoke api key."""
        current_app.logger.debug('<revoke_key ')
        check_auth(one_of_roles=(ADMIN, STAFF), org_id=org_id)
        consumer_endpoint: str = current_app.config.get('API_GW_CONSUMERS_API_URL')
        gw_api_key: str = current_app.config.get('API_GW_KEY')
        env = None
        # Find the environment for this key, based on it consumer changes.
        for key in cls.get_api_keys(org_id)['consumer']['consumerKey']:
            if key['apiKey'] == api_key:
                env = 'prod' if key['environment'] == 'prod' else 'sandbox'
                break
        if not env:
            raise BusinessException(Error.DATA_NOT_FOUND, Exception())

        email_id = cls._get_email_id(org_id, env)

        RestService.patch(
            f'{consumer_endpoint}/mc/v1/consumers/{email_id}/apikeys/{api_key}?action=revoke',
            additional_headers={'x-apikey': gw_api_key},
            data=dict(apiAccess='ALL_API'),
            generate_token=False
        )

    @classmethod
    def get_api_keys(cls, org_id: int) -> List[Dict[str, any]]:
        """Get all api keys."""
        current_app.logger.debug('<get_api_keys ')
        consumer_endpoint: str = current_app.config.get('API_GW_CONSUMERS_API_URL')
        gw_api_key: str = current_app.config.get('API_GW_KEY')
        check_auth(one_of_roles=(ADMIN, STAFF), org_id=org_id)
        api_keys_response = {'consumer': {'consumerKey': []}}
        for email in cls._get_email_id(org_id, 'sandbox'), cls._get_email_id(org_id, 'prod'):

            try:
                consumers_response = RestService.get(
                    f'{consumer_endpoint}/mc/v1/consumers/{email}',
                    additional_headers={'x-apikey': gw_api_key}
                )
                keys = consumers_response.json()['consumer']['consumerKey']
                cls._filter_and_add_keys(api_keys_response, keys)
            except HTTPError as exc:
                if exc.response.status_code != 404:  # If consumer doesn't exist
                    raise exc

        return api_keys_response

    @classmethod
    def _filter_and_add_keys(cls, api_keys_response, keys):
        if isinstance(keys, dict):
            if keys['keyStatus'] == 'approved':
                api_keys_response['consumer']['consumerKey'].append(keys)
        elif isinstance(keys, list):
            for key in keys:
                if key['keyStatus'] == 'approved':
                    api_keys_response['consumer']['consumerKey'].append(key)

    @classmethod
    def _get_email_id(cls, org_id, env) -> str:
        if current_app.config.get('API_GW_CONSUMER_EMAIL', None) is not None:
            return current_app.config.get('API_GW_CONSUMER_EMAIL')

        api_gw_email_suffix: str = current_app.config.get('API_GW_EMAIL_SUFFIX')
        id_suffix = '' if env == 'prod' else '-sandbox'
        email_id = f'{org_id}{id_suffix}@{api_gw_email_suffix}'
        return email_id

    @classmethod
    def _consumer_exists(cls, email):
        """Return if customer exists with this email."""
        consumer_endpoint: str = current_app.config.get('API_GW_CONSUMERS_API_URL')
        gw_api_key: str = current_app.config.get('API_GW_KEY')
        try:
            RestService.get(
                f'{consumer_endpoint}/mc/v1/consumers/{email}',
                additional_headers={'x-apikey': gw_api_key}
            )
        except HTTPError as exc:
            if exc.response.status_code == 404:  # If consumer doesn't exist
                return False
            raise exc

        return True

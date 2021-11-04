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

from auth_api.models.org import Org as OrgModel
from auth_api.services.authorization import check_auth
from auth_api.services.keycloak import KeycloakService
from auth_api.services.rest_service import RestService
from auth_api.utils.api_gateway import generate_client_representation
from auth_api.utils.constants import GROUP_ACCOUNT_HOLDERS, GROUP_API_GW_USERS
from auth_api.utils.roles import ADMIN, STAFF


class ApiGateway:
    """Manages all aspects of the API gateway integration."""

    @classmethod
    def create_key(cls, org_id: int, request_json: Dict[str, str]):
        """Create a key for the account."""
        current_app.logger.debug('<create_key ')
        env = request_json.get('environment', 'sandbox')
        name = request_json.get('keyName')
        org: OrgModel = OrgModel.find_by_id(org_id)
        # first find if there is a consumer created for this account.
        consumer_endpoint: str = current_app.config.get('API_GW_CONSUMERS_API_URL')
        gw_api_key = current_app.config.get('API_GW_KEY') if env == 'prod' else current_app.config.get(
            'API_GW_NON_PROD_KEY')
        email = cls._get_email_id(org_id)

        if not org.has_api_access:  # If the account doesn't have api access, add it
            client_rep = generate_client_representation(org_id, current_app.config.get('API_GW_KC_CLIENT_ID_PATTERN'))
            KeycloakService.create_client(client_rep)
            service_account = KeycloakService.get_service_account_user(client_rep.get('id'))
            KeycloakService.add_user_to_group(service_account.get('id'), GROUP_API_GW_USERS)
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
            org.has_api_access = True
            org.save()
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

        return api_key_response.json()

    @classmethod
    def revoke_key(cls, org_id: int, api_key: str):
        """Revoke api key."""
        current_app.logger.debug('<revoke_key ')
        check_auth(one_of_roles=(ADMIN, STAFF), org_id=org_id)
        consumer_endpoint: str = current_app.config.get('API_GW_CONSUMERS_API_URL')
        gw_api_key: str = current_app.config.get('API_GW_KEY')
        email_id = cls._get_email_id(org_id)

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
        email_id = cls._get_email_id(org_id)
        try:
            consumers_response = RestService.get(
                f'{consumer_endpoint}/mc/v1/consumers/{email_id}',
                additional_headers={'x-apikey': gw_api_key}
            )
            api_keys = consumers_response.json()
        except HTTPError as exc:
            if exc.response.status_code == 404:
                api_keys = {}
            else:
                raise exc

        return api_keys

    @classmethod
    def _get_email_id(cls, org_id) -> str:
        if current_app.config.get('API_GW_CONSUMER_EMAIL', None) is not None:
            return current_app.config.get('API_GW_CONSUMER_EMAIL')

        api_gw_email_suffix: str = current_app.config.get('API_GW_EMAIL_SUFFIX')
        email_id = f'{org_id}@{api_gw_email_suffix}'
        return email_id

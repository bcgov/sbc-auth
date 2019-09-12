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
"""The Authorization service.

This module is to handle authorization related queries.
"""
from typing import Dict

from auth_api.models.views.authorization import Authorization as AuthorizationView
from auth_api.schemas.authorization import AuthorizationSchema


class Authorization:
    """This module is to handle authorization related queries.
    The authorization model as such doesn't exist, so this is a class where we can map all the relationship to query
    user authorizations.
    """

    def __init__(self, model):
        """Return an Authorization Service."""
        self._model = model

    @staticmethod
    def get_user_authorizations_for_entity(token_info: Dict, business_identifier: str):
        """Get User authorizations for the entity."""
        auth_response = {}
        if token_info.get('loginSource', None) == 'PASSCODE':
            if token_info.get('username', None).upper() == business_identifier.upper():
                auth_response = {'role': 'OWNER'}
        elif 'staff' in token_info.get('realm_access', []).get('roles', []):
            auth_response = {'role': 'STAFF'}
        else:
            keycloak_guid = token_info.get('sub', None)
            auth = AuthorizationView.find_user_authorization_by_business_number(keycloak_guid, business_identifier)
            if auth:
                auth_response = Authorization(auth).as_dict(exclude=['business_identifier'])
        return auth_response

    @staticmethod
    def get_user_authorizations(keycloak_guid: str):
        """Get all user authorizations."""
        authorizations_response: Dict = {'authorizations': []}

        authorizations = AuthorizationView.find_all_authorizations_for_user(keycloak_guid)
        if authorizations:
            for auth in authorizations:
                authorizations_response['authorizations'].append(Authorization(auth).as_dict())
        return authorizations_response

    def as_dict(self, exclude: [] = None):
        """Return the authorization as a python dictionary.

        None fields are not included in the dictionary.
        """
        if not exclude:
            exclude = []
        auth_schema = AuthorizationSchema(exclude=exclude)
        return auth_schema.dump(self._model, many=False)

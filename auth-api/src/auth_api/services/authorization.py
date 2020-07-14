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

from flask import abort

from auth_api.models.views.authorization import Authorization as AuthorizationView
from auth_api.utils.roles import STAFF, Role


class Authorization:
    """This module is to handle authorization related queries.

    The authorization model as such doesn't exist, so this is a class where we can map all the relationship to query
    user authorizations.
    """

    def __init__(self, model):
        """Return an Authorization Service."""
        self._model = model

    @staticmethod
    def get_user_authorizations_for_entity(token_info: Dict, business_identifier: str, expanded: bool = False):
        """Get User authorizations for the entity."""
        auth_response = {}
        auth = None
        token_roles = token_info.get('realm_access').get('roles')

        if Role.STAFF.value in token_roles:
            if expanded:
                # Query Authorization view by business identifier
                auth = AuthorizationView.find_user_authorization_by_business_number(business_identifier)
                auth_response = Authorization(auth).as_dict(expanded)
            auth_response['roles'] = token_roles

        elif Role.SYSTEM.value in token_roles:
            # a service account in keycloak should have product_code claim setup.
            keycloak_product_code = token_info.get('product_code', None)
            if keycloak_product_code:
                auth = AuthorizationView.find_user_authorization_by_business_number_and_product(business_identifier,
                                                                                                keycloak_product_code)
                if auth:
                    auth_response = Authorization(auth).as_dict(expanded)
                    auth_response['roles'] = ['edit', 'view']
        else:
            keycloak_guid = token_info.get('sub', None)
            if business_identifier and keycloak_guid:
                auth = AuthorizationView.find_user_authorization_by_business_number(business_identifier, keycloak_guid)

            if auth:
                auth_response = Authorization(auth).as_dict(expanded)
                auth_response['roles'] = ['edit', 'view']

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

    @staticmethod
    def get_account_authorizations_for_product(keycloak_guid: str, account_id: str, product_code: str,
                                               expanded: bool = False):
        """Get account authorizations for the product."""
        authorization = AuthorizationView.find_account_authorization_by_org_id_and_product_for_user(keycloak_guid,
                                                                                                    account_id,
                                                                                                    product_code)
        auth_response = Authorization(authorization).as_dict(expanded)
        auth_response['roles'] = authorization.roles.split(',') if authorization and authorization.roles else []

        return auth_response

    def as_dict(self, expanded: bool = False):
        """Return the authorization as a python dictionary."""
        auth_dict = {}

        if not self._model:
            return auth_dict

        auth_dict['orgMembership'] = self._model.org_membership

        # If the request is for expanded authz return more info
        if expanded:
            auth_dict['business'] = {
                'folioNumber': self._model.folio_number,
                'name': self._model.entity_name
            }
            auth_dict['account'] = {
                'id': self._model.org_id,
                'name': self._model.org_name,
                'accountType': self._model.org_type,
                'paymentPreference': {
                    'methodOfPayment': self._model.preferred_payment_code,
                    'bcOnlineUserId': self._model.bcol_user_id,
                    'bcOnlineAccountId': self._model.bcol_account_id
                }
            }
        return auth_dict


def check_auth(token_info: Dict, **kwargs):
    """Check if user is authorized to perform action on the service."""
    if Role.STAFF.value in token_info.get('realm_access').get('roles'):
        _check_for_roles(STAFF, kwargs)
    elif Role.SYSTEM.value in token_info.get('realm_access').get('roles'):
        business_identifier = kwargs.get('business_identifier', None)
        org_identifier = kwargs.get('org_id', None)

        product_code_in_jwt = token_info.get('product_code', None)
        if product_code_in_jwt is None:
            # product code must be present in jwt
            abort(403)

        if business_identifier:
            auth = Authorization.get_user_authorizations_for_entity(token_info, business_identifier)
        elif org_identifier:
            auth = Authorization.get_account_authorizations_for_product(token_info.get('sub', None),
                                                                        org_identifier,
                                                                        product_code_in_jwt)
        if auth is None:
            abort(403)
        return
    else:
        business_identifier = kwargs.get('business_identifier', None)
        org_identifier = kwargs.get('org_id', None)
        if business_identifier:
            auth = Authorization.get_user_authorizations_for_entity(token_info, business_identifier)
        elif org_identifier:
            auth_record = AuthorizationView.find_user_authorization_by_org_id(token_info.get('sub', None),
                                                                              org_identifier)
            auth = Authorization(auth_record).as_dict() if auth_record else None

        _check_for_roles(auth.get('orgMembership', None) if auth else None, kwargs)


def _check_for_roles(role: str, kwargs):
    is_authorized: bool = False
    # If role is found
    if role:
        if kwargs.get('one_of_roles', None):
            is_authorized = role in kwargs.get('one_of_roles')
        if kwargs.get('disabled_roles', None):
            is_authorized = role not in kwargs.get('disabled_roles')
        if kwargs.get('equals_role', None):
            is_authorized = (role == kwargs.get('equals_role'))

    if not is_authorized:
        abort(403)

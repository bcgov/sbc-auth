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
from auth_api.utils.roles import OWNER, STAFF, Role, STAFF_ADMIN


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
                auth_response = {
                    'orgMembership': OWNER,
                    'roles': ['edit', 'view']
                }
        elif 'staff' in token_info.get('realm_access').get('roles'):
            auth_response = {
                'roles': ['edit', 'view']
            }
        elif Role.SYSTEM.value in token_info.get('realm_access').get('roles'):
            # a service account in keycloak should have corp_type claim setup.
            keycloak_corp_type = token_info.get('corp_type', None)
            if keycloak_corp_type:
                auth = AuthorizationView.find_user_authorization_by_business_number_and_corp_type(business_identifier,
                                                                                                  keycloak_corp_type)
                if auth:
                    auth_response = Authorization(auth).as_dict()
                    auth_response['roles'] = ['edit', 'view']
        else:
            keycloak_guid = token_info.get('sub', None)
            auth = AuthorizationView.find_user_authorization_by_business_number(keycloak_guid, business_identifier)
            if auth:
                auth_response = Authorization(auth).as_dict()
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
    def get_account_authorizations_for_product(keycloak_guid: str, account_id: str, product_code: str):
        """Get account authorizations for the product."""
        auth_response: Dict = {'roles': []}
        authorization = AuthorizationView.find_account_authorization_by_org_id_and_product_for_user(keycloak_guid,
                                                                                                    account_id,
                                                                                                    product_code)
        auth_response['roles'] = authorization.roles.split(',') if authorization and authorization.roles else []
        return auth_response

    def as_dict(self):
        """Return the authorization as a python dictionary."""
        auth_dict = {
            'orgMembership': self._model.org_membership,
            'business': {
                'folioNumber': self._model.folio_number,
                'name': self._model.entity_name
            },
            'account': {
                'id': self._model.org_id,
                'name': self._model.org_name,
                'paymentPreference': {
                    'methodOfPayment': self._model.preferred_payment_code,
                    'bcOnlineUserId': self._model.bcol_user_id,
                    'bcOnlineAccountId': self._model.bcol_account_id
                }
            }
        }
        return auth_dict

def check_auth(token_info: Dict, **kwargs):
    """Check if user is authorized to perform action on the service."""
    if 'staff_admin' in token_info.get('realm_access').get('roles'):
        # Staff admin should get all access as of Staff
        if STAFF in kwargs.get('one_of_roles', []) and STAFF_ADMIN not in kwargs.get('one_of_roles', None):
            kwargs.get('one_of_roles').append(STAFF_ADMIN)
        if kwargs.get('equals_role', None) == STAFF:
            kwargs.pop('equals_role', None)
            kwargs['one_of_roles'] = (STAFF, STAFF_ADMIN)
        _check_for_roles(STAFF_ADMIN, kwargs)
    elif 'staff' in token_info.get('realm_access').get('roles'):
        _check_for_roles(STAFF, kwargs)
    elif Role.SYSTEM.value in token_info.get('realm_access').get('roles') \
            and not token_info.get('loginSource', None) == 'PASSCODE':
        corp_type_in_jwt = token_info.get('corp_type', None)
        if corp_type_in_jwt is None:
            # corp type must be present in jwt
            abort(403)
        business_identifier = kwargs.get('business_identifier', None)
        org_identifier = kwargs.get('org_id', None)
        auth = None
        if business_identifier:
            auth = Authorization.get_user_authorizations_for_entity(token_info, business_identifier)
        elif org_identifier:
            auth_record = AuthorizationView.find_user_authorization_by_org_id_and_corp_type(org_identifier,
                                                                                            corp_type_in_jwt)
            auth = Authorization(auth_record).as_dict() if auth_record else None
        if auth is None:
            abort(403)
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

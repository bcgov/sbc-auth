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
from typing import Dict, Optional

from flask import abort, current_app

from auth_api.models.views.authorization import Authorization as AuthorizationView
from auth_api.services.permissions import Permissions as PermissionsService
from auth_api.utils.enums import ProductTypeCode as ProductTypeCodeEnum
from auth_api.utils.roles import STAFF, Role
from auth_api.utils.user_context import UserContext, user_context


class Authorization:
    """This module is to handle authorization related queries.

    The authorization model as such doesn't exist, so this is a class where we can map all the relationship to query
    user authorizations.
    """

    def __init__(self, model):
        """Return an Authorization Service."""
        self._model = model

    @staticmethod
    @user_context
    def get_account_authorizations_for_org(account_id: str, corp_type_code: Optional[str],
                                           expanded: bool = False, **kwargs):
        """Get User authorizations for the org."""
        user_from_context: UserContext = kwargs['user_context']
        auth_response = {}
        auth = None
        token_roles = user_from_context.roles

        current_app.logger.debug(f'token roles=:{token_roles}')

        # todo the service account level access has not been defined
        if Role.STAFF.value in token_roles:
            if expanded:
                # Query Authorization view by business identifier
                auth = AuthorizationView.find_authorization_for_admin_by_org_id(account_id)
                auth_response = Authorization(auth).as_dict(expanded)
            auth_response['roles'] = token_roles
            current_app.logger.debug(f'staff roles=:{token_roles}')
        else:
            keycloak_guid = user_from_context.sub
            account_id_claim = user_from_context.account_id_claim
            # check product based auth auth org based auth
            check_product_based_auth = Authorization._is_product_based_auth(corp_type_code)
            if check_product_based_auth:
                if account_id_claim:
                    current_app.logger.debug(f'auth view product - account_id_claim, corp_type_code=:{account_id_claim} {corp_type_code}')
                    auth = AuthorizationView.find_account_authorization_by_org_id_and_product(account_id_claim,
                                                                                              corp_type_code)
                else:
                    current_app.logger.debug(f'auth view, product based, keycloak, account_id, corp_type_code:{keycloak_guid} {account_id} {corp_type_code}')
                    auth = AuthorizationView.find_account_authorization_by_org_id_and_product_for_user(
                        keycloak_guid, account_id, corp_type_code
                    )
            else:
                if account_id_claim and account_id == int(account_id_claim):
                    current_app.logger.debug(f'auth view account_id claim=:{account_id_claim}')
                    auth = AuthorizationView.find_authorization_for_admin_by_org_id(account_id_claim)
                elif account_id and keycloak_guid:
                    current_app.logger.debug(f'auth view, keycloak guid, account_id=:{keycloak_guid} , {account_id}')
                    auth = AuthorizationView.find_user_authorization_by_org_id(keycloak_guid, account_id)
            auth_response['roles'] = []
            if auth:
                current_app.logger.debug(f'if auth true permissions, status_code, org_membership:{auth.status_code} , {auth.org_membership}')
                permissions = PermissionsService.get_permissions_for_membership(auth.status_code,
                                                                                auth.org_membership)
                auth_response = Authorization(auth).as_dict(expanded)
                auth_response['roles'] = permissions
                current_app.logger.debug(f'if auth roles:{permissions}')

        return auth_response

    @staticmethod
    @user_context
    def get_user_authorizations_for_entity(business_identifier: str, expanded: bool = False, **kwargs):
        """Get User authorizations for the entity."""
        user_from_context: UserContext = kwargs['user_context']
        auth_response = {}
        auth = None
        token_roles = user_from_context.roles
        current_app.logger.debug(f'check roles=:{token_roles}')
        if Role.STAFF.value in token_roles:
            if expanded:
                # Query Authorization view by business identifier
                auth = AuthorizationView.find_user_authorization_by_business_number(business_identifier, is_staff=True)
                auth_response = Authorization(auth).as_dict(expanded)
            auth_response['roles'] = token_roles

        elif Role.SYSTEM.value in token_roles:
            # a service account in keycloak should have product_code claim setup.
            keycloak_product_code = user_from_context.token_info.get('product_code', None)
            if keycloak_product_code:
                auth = AuthorizationView.find_user_authorization_by_business_number_and_product(business_identifier,
                                                                                                keycloak_product_code)
                if auth:
                    auth_response = Authorization(auth).as_dict(expanded)
                    permissions = PermissionsService.get_permissions_for_membership(auth.status_code, 'SYSTEM')
                    auth_response['roles'] = permissions
        else:
            keycloak_guid = user_from_context.sub
            if business_identifier and keycloak_guid:
                auth = AuthorizationView.find_user_authorization_by_business_number(
                    business_identifier=business_identifier,
                    keycloak_guid=keycloak_guid,
                    org_id=user_from_context.account_id
                )

            if auth:
                permissions = PermissionsService.get_permissions_for_membership(auth.status_code, auth.org_membership)
                auth_response = Authorization(auth).as_dict(expanded)
                auth_response['roles'] = permissions

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
    @user_context
    def get_account_authorizations_for_product(account_id: str, product_code: str, expanded: bool = False, **kwargs):
        """Get account authorizations for the product."""
        user_from_context: UserContext = kwargs['user_context']
        account_id_claim = user_from_context.account_id
        if account_id_claim:
            auth = AuthorizationView.find_account_authorization_by_org_id_and_product(
                account_id_claim, product_code
            )
        else:
            auth = AuthorizationView.find_account_authorization_by_org_id_and_product_for_user(
                user_from_context.sub, account_id, product_code
            )
        auth_response = Authorization(auth).as_dict(expanded)
        auth_response['roles'] = []
        if auth:
            permissions = PermissionsService.get_permissions_for_membership(auth.status_code, auth.org_membership)
            auth_response['roles'] = permissions

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
                    'bcOnlineUserId': self._model.bcol_user_id,
                    'bcOnlineAccountId': self._model.bcol_account_id
                }
            }
        return auth_dict

    @staticmethod
    def _is_product_based_auth(product_code):

        check_product_based_auth = False
        if product_code:
            from auth_api.services.products import \
                Product as ProductService  # pylint:disable=cyclic-import, import-outside-toplevel
            product_type: str = ProductService.find_product_type_by_code(product_code)
            # TODO should we reject if the product code is unknown??
            if product_type == ProductTypeCodeEnum.PARTNER.value:  # PARTNERS needs product based auth
                check_product_based_auth = True
        return check_product_based_auth


@user_context
def check_auth(**kwargs):
    """Check if user is authorized to perform action on the service."""
    user_from_context: UserContext = kwargs['user_context']
    if user_from_context.is_staff():
        _check_for_roles(STAFF, kwargs)
    elif user_from_context.is_system():
        business_identifier = kwargs.get('business_identifier', None)
        org_identifier = kwargs.get('org_id', None)

        product_code_in_jwt = user_from_context.token_info.get('product_code', None)
        if product_code_in_jwt is None:
            # product code must be present in jwt
            abort(403)
        if product_code_in_jwt == 'ALL':  # Product code for super admin service account (sbc-auth-admin)
            return

        if business_identifier:
            auth = Authorization.get_user_authorizations_for_entity(business_identifier)
        elif org_identifier:
            auth = Authorization.get_account_authorizations_for_product(org_identifier, product_code_in_jwt)
        if auth is None:
            abort(403)
        return
    else:
        business_identifier = kwargs.get('business_identifier', None)
        org_identifier = kwargs.get('org_id', None) or user_from_context.account_id
        if business_identifier:
            auth = Authorization.get_user_authorizations_for_entity(business_identifier)
        elif org_identifier:
            # If the account id is part of claim (api gw users), then no need to lookup using keycloak guid.
            if user_from_context.account_id_claim and \
                    int(user_from_context.account_id_claim) == kwargs.get('org_id', None):
                auth_record = AuthorizationView.find_authorization_for_admin_by_org_id(user_from_context.account_id)
            else:
                auth_record = AuthorizationView.find_user_authorization_by_org_id(user_from_context.sub, org_identifier)
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

# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the Membership service.

Test suite to ensure that the Membership service routines are working as expected.
"""

from auth_api.models import MembershipStatusCode as MembershipStatusCodeModel
from auth_api.services import Membership as MembershipService
from auth_api.services import Org as OrgService
from auth_api.services.keycloak import KeycloakConfig, KeycloakService
from auth_api.utils.constants import GROUP_ACCOUNT_HOLDERS
from auth_api.utils.roles import Status
from tests.utilities.factory_scenarios import (
    KeycloakScenario, TestOrgInfo, TestUserInfo)
from tests.utilities.factory_utils import (
    factory_membership_model,
    factory_user_model)


def test_accept_invite_adds_group_to_the_user(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that accepting an invite adds group to the user."""
    # Create a user in keycloak
    keycloak_service = KeycloakService()
    keycloak_service.add_user(KeycloakScenario.create_user_request)
    kc_user = keycloak_service.get_user_by_username(KeycloakScenario.create_user_request.get('username'))
    user = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user.get('id')))

    # Patch token info
    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {
            'sub': str(kc_user.get('id')),
            'username': 'public_user',
            'realm_access': {
                'roles': [
                ]
            }
        }

    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService._get_token_info', token_info)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    # Create another user
    keycloak_service.add_user(KeycloakScenario.create_user_request_2)
    kc_user2 = keycloak_service.get_user_by_username(KeycloakScenario.create_user_request_2.get('username'))
    user2 = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user2.get('id')))

    # Add a membership to the user for the org created
    factory_membership_model(user2.id, org.as_dict().get('id'), member_type='ADMIN', member_status=4)

    # Find the membership and update to ACTIVE
    membership = MembershipService.get_membership_for_org_and_user(org.as_dict().get('id'), user2.id)
    active_membership_status = MembershipStatusCodeModel.get_membership_status_by_code(Status.ACTIVE.name)
    updated_fields = {'membership_status': active_membership_status}
    MembershipService(membership).update_membership(updated_fields=updated_fields, token_info=token_info())

    user_groups = KeycloakConfig().get_keycloak_admin().get_user_groups(user_id=kc_user2.get('id'))
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups


def test_remove_member_removes_group_to_the_user(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that accepting an invite adds group to the user."""
    # Create a user in keycloak
    keycloak_service = KeycloakService()
    keycloak_service.add_user(KeycloakScenario.create_user_request)
    kc_user = keycloak_service.get_user_by_username(KeycloakScenario.create_user_request.get('username'))
    user = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user.get('id')))

    # Patch token info
    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {
            'sub': str(kc_user.get('id')),
            'username': 'public_user',
            'realm_access': {
                'roles': [
                ]
            }
        }

    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService._get_token_info', token_info)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    # Create another user
    keycloak_service.add_user(KeycloakScenario.create_user_request_2)
    kc_user2 = keycloak_service.get_user_by_username(KeycloakScenario.create_user_request_2.get('username'))
    user2 = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user2.get('id')))

    # Add a membership to the user for the org created
    factory_membership_model(user2.id, org.as_dict().get('id'), member_type='ADMIN', member_status=4)

    # Find the membership and update to ACTIVE
    membership = MembershipService.get_membership_for_org_and_user(org.as_dict().get('id'), user2.id)
    active_membership_status = MembershipStatusCodeModel.get_membership_status_by_code(Status.ACTIVE.name)
    updated_fields = {'membership_status': active_membership_status}
    MembershipService(membership).update_membership(updated_fields=updated_fields, token_info=token_info())

    user_groups = KeycloakConfig().get_keycloak_admin().get_user_groups(user_id=kc_user2.get('id'))
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups

    # Find the membership and update to INACTIVE
    active_membership_status = MembershipStatusCodeModel.get_membership_status_by_code(Status.INACTIVE.name)
    updated_fields = {'membership_status': active_membership_status}
    MembershipService(membership).update_membership(updated_fields=updated_fields, token_info=token_info())

    user_groups = KeycloakConfig().get_keycloak_admin().get_user_groups(user_id=kc_user2.get('id'))
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS not in groups

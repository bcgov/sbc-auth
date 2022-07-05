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

from unittest.mock import ANY, patch
from auth_api.models import MembershipStatusCode as MembershipStatusCodeModel
from auth_api.models.dataclass import Activity
from auth_api.services import ActivityLogPublisher
from auth_api.services import Membership as MembershipService
from auth_api.services import Org as OrgService
from auth_api.services.keycloak import KeycloakService
from auth_api.utils.constants import GROUP_ACCOUNT_HOLDERS
from auth_api.utils.enums import ActivityAction, ProductCode, Status
from tests.utilities.factory_scenarios import KeycloakScenario, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import factory_membership_model, factory_product_model, factory_user_model


def test_accept_invite_adds_group_to_the_user(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that accepting an invite adds group to the user."""
    # Create a user in keycloak
    keycloak_service = KeycloakService()
    request = KeycloakScenario.create_user_request()
    keycloak_service.add_user(request, return_if_exists=True)
    kc_user = keycloak_service.get_user_by_username(request.user_name)
    user = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user.id))

    # Patch token info
    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {
            'sub': str(kc_user.id),
            'username': 'public_user',
            'realm_access': {
                'roles': [
                    'edit'
                ]
            },
            'product_code': ProductCode.BUSINESS.value
        }

    monkeypatch.setattr('auth_api.utils.user_context._get_token_info', token_info)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    # Create another user
    request = KeycloakScenario.create_user_request()
    keycloak_service.add_user(request, return_if_exists=True)
    kc_user2 = keycloak_service.get_user_by_username(request.user_name)
    user2 = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user2.id))

    # Add a membership to the user for the org created
    factory_membership_model(user2.id, org.as_dict().get('id'), member_type='COORDINATOR', member_status=4)

    # Add a product to org
    factory_product_model(org.as_dict().get('id'), product_code=ProductCode.BUSINESS.value)

    # Find the membership and update to ACTIVE
    membership = MembershipService.get_membership_for_org_and_user(org.as_dict().get('id'), user2.id)
    active_membership_status = MembershipStatusCodeModel.get_membership_status_by_code(Status.ACTIVE.name)
    updated_fields = {'membership_status': active_membership_status}
    MembershipService(membership).update_membership(updated_fields=updated_fields, token_info=token_info())

    user_groups = keycloak_service.get_user_groups(user_id=kc_user2.id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups


def test_remove_member_removes_group_to_the_user(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that accepting an invite adds group to the user."""
    # Create a user in keycloak
    keycloak_service = KeycloakService()
    request = KeycloakScenario.create_user_request()
    keycloak_service.add_user(request, return_if_exists=True)
    kc_user = keycloak_service.get_user_by_username(request.user_name)
    user = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user.id))

    # Patch token info
    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {
            'sub': str(kc_user.id),
            'username': 'public_user',
            'realm_access': {
                'roles': [
                    'edit'
                ]
            },
            'product_code': ProductCode.BUSINESS.value
        }

    monkeypatch.setattr('auth_api.utils.user_context._get_token_info', token_info)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    # Create another user
    request = KeycloakScenario.create_user_request()
    keycloak_service.add_user(request, return_if_exists=True)
    kc_user2 = keycloak_service.get_user_by_username(request.user_name)
    user2 = factory_user_model(TestUserInfo.get_user_with_kc_guid(kc_guid=kc_user2.id))

    # Add a membership to the user for the org created
    factory_membership_model(user2.id, org.as_dict().get('id'), member_type='COORDINATOR', member_status=4)

    # Add a product to org
    factory_product_model(org.as_dict().get('id'), product_code=ProductCode.BUSINESS.value)

    # Find the membership and update to ACTIVE
    membership = MembershipService.get_membership_for_org_and_user(org.as_dict().get('id'), user2.id)
    active_membership_status = MembershipStatusCodeModel.get_membership_status_by_code(Status.ACTIVE.name)
    updated_fields = {'membership_status': active_membership_status}
    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        MembershipService(membership).update_membership(updated_fields=updated_fields, token_info=token_info())
        mock_alp.assert_called_with(Activity(action=ActivityAction.APPROVE_TEAM_MEMBER.value,
                                             org_id=ANY, name=ANY, id=ANY,
                                             value=ANY))
    user_groups = keycloak_service.get_user_groups(user_id=kc_user2.id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS in groups

    # Deactivate Membership
    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        MembershipService(membership).deactivate_membership(token_info=token_info())
        mock_alp.assert_called_with(Activity(action=ActivityAction.REMOVE_TEAM_MEMBER.value,
                                             org_id=ANY, name=ANY, id=ANY,
                                             value=ANY))

    # ACTIVE
    active_membership_status = MembershipStatusCodeModel.get_membership_status_by_code(Status.ACTIVE.name)
    updated_fields = {'membership_status': active_membership_status}
    MembershipService(membership).update_membership(updated_fields=updated_fields, token_info=token_info())

    # Find the membership and update to INACTIVE
    active_membership_status = MembershipStatusCodeModel.get_membership_status_by_code(Status.INACTIVE.name)
    updated_fields = {'membership_status': active_membership_status}
    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        MembershipService(membership).update_membership(updated_fields=updated_fields, token_info=token_info())
        mock_alp.assert_called_with(Activity(action=ActivityAction.REMOVE_TEAM_MEMBER.value,
                                             org_id=ANY, name=ANY, id=ANY,
                                             value=ANY))

    user_groups = keycloak_service.get_user_groups(user_id=kc_user2.id)
    groups = []
    for group in user_groups:
        groups.append(group.get('name'))
    assert GROUP_ACCOUNT_HOLDERS not in groups

    MembershipService(membership).deactivate_membership()

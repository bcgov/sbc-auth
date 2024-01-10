# Copyright © 2023 Province of British Columbia
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
"""Tests for the Invitation service authentication / user context.

Test suite to ensure that the Invitation service authentication / login source checks are correct.
"""
from unittest.mock import ANY, patch

import mock
import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Invitation as InvitationModel
from auth_api.models.dataclass import Activity
from auth_api.services import ActivityLogPublisher
from auth_api.services import Invitation as InvitationService
from auth_api.services import Membership as MembershipService
from auth_api.services import Org as OrgService
from auth_api.services import User
from auth_api.utils.enums import AccessType, ActivityAction, InvitationStatus, LoginSource
from auth_api.utils.user_context import UserContext, user_context
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import factory_invitation, factory_user_model, patch_token_info
from tests.conftest import mock_token


@user_context
def assert_token_user_context(login_source: str = None, **kwargs):
    """Assert user_context information with token_info."""
    user_from_context: UserContext = kwargs['user_context']

    assert user_from_context is not None

    token_info = user_from_context.token_info
    assert token_info is not None

    # When trying to use patch_token_info take note of the token attribute naming as they differ from the user_context
    # e.g. loginSource --> login_source
    assert user_from_context.login_source == token_info.get('loginSource')
    assert user_from_context.first_name == token_info.get('firstname')
    assert user_from_context.last_name == token_info.get('lastname')
    assert user_from_context.sub == token_info.get('sub')

    # Assert for a specific expected login_source
    if login_source:
        assert user_from_context.login_source == login_source
        assert token_info.get('loginSource') == login_source


def test_token_user_context(session, auth_mock, monkeypatch):
    """Assert and document expected behavior using patch_token_info with user context login_source for tests."""
    # In order to fully mock out auth with user_context, auth_mock and monkeypatch is used in the function params
    # Create an initial user in the db to work with
    user = factory_user_model(TestUserInfo.user1)

    # We are expecting empty user context values and token info as patch_token_info has not been used
    assert_token_user_context()

    # We can use existing data sets for patch token
    patch_token_info(TestJwtClaims.staff_admin_role, monkeypatch)
    assert_token_user_context(LoginSource.STAFF.value)

    # Replace token_info with the specified attributes using the user model data as reference
    # The sub or idp_userid is usually required to reference an existing user within service logic in queries etc
    # patch_token_info need to be called before your service call to set the user context / token info you are testing
    # against
    patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid,
                      'loginSource': LoginSource.BCSC.value}, monkeypatch)
    assert_token_user_context(LoginSource.BCSC.value)

    # This usage of patching replaces the previous values, only loginSource will be set
    # Ensure all relevant values are part of your patch payload if you are getting user related errors
    patch_token_info({'loginSource': LoginSource.BCEID.value}, monkeypatch)
    assert_token_user_context(LoginSource.BCEID.value)


@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
def test_change_authentication_subsequent_invites(session, auth_mock, keycloak_mock, monkeypatch):
    """Assert that changing org authentication method changes new invitation required login source."""
    user_with_token = TestUserInfo.user_tester
    user_with_token['keycloak_guid'] = TestJwtClaims.tester_role['sub']
    user_with_token['idp_userid'] = TestJwtClaims.tester_role['idp_userid']
    inviter_user = factory_user_model(user_info=user_with_token)

    patch_token_info(TestJwtClaims.tester_role, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org1, user_id=inviter_user.id)
    org_dictionary = org.as_dict()

    # Org with access type of 'REGULAR' will create an invitation with login source BCSC
    assert org_dictionary['access_type'] == AccessType.REGULAR.value

    # Change authentication method to BCSC
    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        OrgService.update_login_option(org_dictionary['id'], LoginSource.BCSC.value)
    mock_alp.assert_called_with(Activity(action=ActivityAction.AUTHENTICATION_METHOD_CHANGE.value,
                                         org_id=ANY, name=ANY, id=ANY, value=LoginSource.BCSC.value))

    with patch.object(InvitationService, 'send_invitation', return_value=None):
        # Create invitation that has BCSC login source
        with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
            invitation_bcsc_info = factory_invitation(org_dictionary['id'])
            invitation_bcsc = InvitationService.create_invitation(invitation_bcsc_info, User(inviter_user), '')
            mock_alp.assert_called_with(Activity(action=ActivityAction.INVITE_TEAM_MEMBER.value,
                                                 org_id=ANY, name=invitation_bcsc_info['recipientEmail'], id=ANY,
                                                 value='USER'))

            # Should be BCSC login source
            invitation_model = InvitationModel.find_invitation_by_id(invitation_bcsc.as_dict()['id'])
            assert invitation_model.login_source == LoginSource.BCSC.value

        # Change authentication method to BCEID
        with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
            OrgService.update_login_option(org_dictionary['id'], LoginSource.BCEID.value)
        mock_alp.assert_called_with(Activity(action=ActivityAction.AUTHENTICATION_METHOD_CHANGE.value,
                                             org_id=ANY, name=ANY, id=ANY, value=LoginSource.BCEID.value))

        # Create another invitation and it should be BCEID login source
        with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
            invitation_bceid_info = factory_invitation(org_dictionary['id'])
            invitation_bceid_info['recipientEmail'] = 'test@test.com'
            invitation_bceid = InvitationService.create_invitation(invitation_bceid_info, User(inviter_user), '')
            mock_alp.assert_called_with(Activity(action=ActivityAction.INVITE_TEAM_MEMBER.value,
                                                 org_id=ANY, name=invitation_bceid_info['recipientEmail'], id=ANY,
                                                 value='USER'))

            # Should be BCEID login source
            invitation_model = InvitationModel.find_invitation_by_id(invitation_bceid.as_dict()['id'])
            assert invitation_model.login_source == LoginSource.BCEID.value


@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
def test_change_authentication_non_govm(session, auth_mock, keycloak_mock, monkeypatch):
    """Assert that non government ministry organization invites can be accepted by different login sources."""
    # inviter/invitee user setup
    inviter_user = factory_user_model(TestUserInfo.user_tester)
    invitee_bcsc_user = factory_user_model(TestUserInfo.user1)
    invitee_bceid_user = factory_user_model(TestUserInfo.user2)

    patch_token_info(TestJwtClaims.tester_role, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=inviter_user.id)
    org_dictionary = org.as_dict()

    # Org with access type of 'REGULAR' will create an invitation with login source BCSC
    assert org_dictionary['access_type'] == AccessType.REGULAR.value

    # Confirm that an invitation with BCSC login source can be accepted as a BCSC user
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        # Create invitation with BCSC source
        with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
            invitation_info = factory_invitation(org_dictionary['id'])
            invitation = InvitationService.create_invitation(invitation_info, User(inviter_user), '')
            invitation_dict = invitation.as_dict()

            mock_alp.assert_called_with(Activity(action=ActivityAction.INVITE_TEAM_MEMBER.value,
                                                 org_id=ANY, name=invitation_info['recipientEmail'], id=ANY,
                                                 value='USER'))

            invitation_model = InvitationModel.find_invitation_by_id(invitation_dict['id'])
            assert invitation_model.login_source == LoginSource.BCSC.value
            assert invitation_model.invitation_status_code == InvitationStatus.PENDING.value

            patch_token_info({'sub': invitee_bcsc_user.keycloak_guid, 'idp_userid': invitee_bcsc_user.idp_userid,
                              'loginSource': LoginSource.BCSC.value}, monkeypatch)
            InvitationService.accept_invitation(invitation_dict['id'], User(invitee_bcsc_user), '')

            invitation_model = InvitationModel.find_invitation_by_id(invitation_dict['id'])
            assert invitation_model.login_source == LoginSource.BCSC.value
            assert invitation_model.invitation_status_code == InvitationStatus.ACCEPTED.value

            patch_token_info(TestJwtClaims.tester_role, monkeypatch)
            members = MembershipService.get_members_for_org(org_dictionary['id'],
                                                            'PENDING_APPROVAL')
            assert members
            assert len(members) == 1

    # Confirm that an invitation with BCSC login source can be accepted as another user login source and
    # updates the invitation login source based on the accepting user login source
    patch_token_info(TestJwtClaims.tester_role, monkeypatch)
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        # Create invitation with BCSC login source
        with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
            invitation_info = factory_invitation(org_dictionary['id'])
            invitation = InvitationService.create_invitation(invitation_info, User(inviter_user), '')
            invitation_dict = invitation.as_dict()

            mock_alp.assert_called_with(Activity(action=ActivityAction.INVITE_TEAM_MEMBER.value,
                                                 org_id=ANY, name=invitation_info['recipientEmail'], id=ANY,
                                                 value='USER'))

            # Confirm invitation is BCSC as per org data
            invitation_model = InvitationModel.find_invitation_by_id(invitation_dict['id'])
            assert invitation_model.login_source == LoginSource.BCSC.value
            assert invitation_model.invitation_status_code == InvitationStatus.PENDING.value

            # Accept invitation as a BCEID user
            patch_token_info({'sub': invitee_bceid_user.keycloak_guid, 'idp_userid': invitee_bceid_user.idp_userid,
                              'loginSource': LoginSource.BCEID.value}, monkeypatch)
            InvitationService.accept_invitation(invitation_dict['id'], User(invitee_bceid_user), '')

            # Confirm invitation login source is updated to BCEID
            invitation_model = InvitationModel.find_invitation_by_id(invitation_dict['id'])
            assert invitation_model.login_source == LoginSource.BCEID.value
            assert invitation_model.invitation_status_code == InvitationStatus.ACCEPTED.value

            patch_token_info(TestJwtClaims.tester_role, monkeypatch)
            members = MembershipService.get_members_for_org(org_dictionary['id'],
                                                            'PENDING_APPROVAL')
            assert members
            assert len(members) == 2


@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
def test_invitation_govm(session, auth_mock, keycloak_mock, monkeypatch):
    """Assert that government ministry organization invites can be accepted by IDIR only."""
    # Users setup
    staff_user = factory_user_model(TestUserInfo.user_staff_admin)
    staff_invitee_user = factory_user_model(TestUserInfo.user1)
    invitee_bcsc_user = factory_user_model(TestUserInfo.user2)
    invitee_bceid_user = factory_user_model(TestUserInfo.user3)

    patch_token_info(TestJwtClaims.staff_admin_role, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org_govm, user_id=staff_user.id)
    org_dictionary = org.as_dict()

    # Org with access type is for government ministry
    assert org_dictionary['access_type'] == AccessType.GOVM.value

    # Confirm that an invitation with BCSC login source can be accepted as a BCSC user
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        # Create invitation with BCSC source
        with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
            invitation_info = factory_invitation(org_dictionary['id'])
            invitation = InvitationService.create_invitation(invitation_info, User(staff_user), '')
            invitation_dict = invitation.as_dict()

            mock_alp.assert_called_with(Activity(action=ActivityAction.INVITE_TEAM_MEMBER.value,
                                                 org_id=ANY, name=invitation_info['recipientEmail'], id=ANY,
                                                 value='USER'))

            invitation_model = InvitationModel.find_invitation_by_id(invitation_dict['id'])
            assert invitation_model.login_source == LoginSource.STAFF.value
            assert invitation_model.invitation_status_code == InvitationStatus.PENDING.value

            # Accept invitation as a BCEID user should raise business exception
            patch_token_info({'sub': invitee_bceid_user.keycloak_guid, 'idp_userid': invitee_bceid_user.idp_userid,
                              'loginSource': LoginSource.BCEID.value}, monkeypatch)
            with pytest.raises(BusinessException) as exception:
                InvitationService.accept_invitation(invitation_dict['id'], User(invitee_bceid_user), '')
            assert exception.value.code == Error.INVALID_USER_CREDENTIALS.name

            # Accept invitation as a BCSC user should raise business exception
            patch_token_info({'sub': invitee_bcsc_user.keycloak_guid, 'idp_userid': invitee_bcsc_user.idp_userid,
                              'loginSource': LoginSource.BCSC.value}, monkeypatch)
            with pytest.raises(BusinessException) as exception:
                InvitationService.accept_invitation(invitation_dict['id'], User(invitee_bcsc_user), '')
            assert exception.value.code == Error.INVALID_USER_CREDENTIALS.name

            # Accept invitation as a staff user should succeed
            patch_token_info({'sub': staff_invitee_user.keycloak_guid, 'idp_userid': staff_invitee_user.idp_userid,
                              'loginSource': LoginSource.STAFF.value}, monkeypatch)
            InvitationService.accept_invitation(invitation_dict['id'], User(staff_invitee_user), '')

            invitation_model = InvitationModel.find_invitation_by_id(invitation_dict['id'])
            assert invitation_model.login_source == LoginSource.STAFF.value
            assert invitation_model.invitation_status_code == InvitationStatus.ACCEPTED.value

            members = MembershipService.get_members_for_org(org_dictionary['id'],
                                                            'ACTIVE')
            assert members
            assert len(members) == 1


@mock.patch('auth_api.services.affiliation_invitation.RestService.get_service_account_token', mock_token)
def test_invitation_anonymous(session, auth_mock, keycloak_mock, monkeypatch):
    """Assert that non government ministry organization invites can be accepted by different login sources."""
    # inviter/invitee user setup
    inviter_user = factory_user_model(TestUserInfo.user_tester)
    invitee_bcsc_user = factory_user_model(TestUserInfo.user1)

    patch_token_info(TestJwtClaims.tester_role, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=inviter_user.id)
    org_dictionary = org.as_dict()

    # Org with access type of 'REGULAR' will create an invitation with login source BCSC
    assert org_dictionary['access_type'] == AccessType.REGULAR.value

    # Confirm that an invitation with BCSC login source can be accepted as a BCSC user
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        # Create invitation with BCSC source
        with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
            invitation_info = factory_invitation(org_dictionary['id'])
            invitation = InvitationService.create_invitation(invitation_info, User(inviter_user), '')
            invitation_dict = invitation.as_dict()

            mock_alp.assert_called_with(Activity(action=ActivityAction.INVITE_TEAM_MEMBER.value,
                                                 org_id=ANY, name=invitation_info['recipientEmail'], id=ANY,
                                                 value='USER'))

            invitation_model = InvitationModel.find_invitation_by_id(invitation_dict['id'])
            assert invitation_model.login_source == LoginSource.BCSC.value
            assert invitation_model.invitation_status_code == InvitationStatus.PENDING.value

            patch_token_info({'sub': invitee_bcsc_user.keycloak_guid,
                              'idp_userid': invitee_bcsc_user.idp_userid}, monkeypatch)
            InvitationService.accept_invitation(invitation_dict['id'], User(invitee_bcsc_user), '')

            invitation_model = InvitationModel.find_invitation_by_id(invitation_dict['id'])
            assert invitation_model.login_source is None
            assert invitation_model.invitation_status_code == InvitationStatus.ACCEPTED.value

            patch_token_info(TestJwtClaims.tester_role, monkeypatch)
            members = MembershipService.get_members_for_org(org_dictionary['id'],
                                                            'PENDING_APPROVAL')
            assert members
            assert len(members) == 1

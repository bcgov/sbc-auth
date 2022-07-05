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
"""Tests for the Invitation service.

Test suite to ensure that the Invitation service routines are working as expected.
"""
from datetime import datetime, timedelta
from unittest.mock import ANY, patch

import pytest
from freezegun import freeze_time
from auth_api.models.dataclass import Activity

import auth_api.services.authorization as auth
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Invitation as InvitationModel
from auth_api.models import InvitationStatus as InvitationStatusModel
from auth_api.services import ActivityLogPublisher
from auth_api.services import Invitation as InvitationService
from auth_api.services import Membership as MembershipService
from auth_api.services import Org as OrgService
from auth_api.services import User
from auth_api.utils.enums import ActivityAction
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import factory_invitation, factory_user_model, patch_token_info


def test_as_dict(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that the Invitation is exported correctly as a dictionary."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        user = factory_user_model()
        patch_token_info({'sub': user.keycloak_guid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
        org_dictionary = org.as_dict()
        invitation_info = factory_invitation(org_dictionary['id'])
        invitation = InvitationService.create_invitation(invitation_info, User(user), '')
        invitation_dictionary = invitation.as_dict()
        assert invitation_dictionary['recipient_email'] == invitation_info['recipientEmail']


def test_create_invitation(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Invitation can be created."""
    with patch.object(InvitationService, 'send_invitation', return_value=None) as mock_notify:
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
        org_dictionary = org.as_dict()
        invitation_info = factory_invitation(org_dictionary['id'])

        with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
            invitation = InvitationService.create_invitation(invitation_info, User(user), '')
            mock_alp.assert_called_with(Activity(action=ActivityAction.INVITE_TEAM_MEMBER.value,
                                        org_id=ANY, name=invitation_info['recipientEmail'], id=ANY,
                                        value='USER'))

        invitation_dictionary = invitation.as_dict()
        assert invitation_dictionary['recipient_email'] == invitation_info['recipientEmail']
        assert invitation_dictionary['id']
        mock_notify.assert_called()


def test_find_invitation_by_id(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Find an existing invitation with the provided id."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
        org_dictionary = org.as_dict()
        invitation_info = factory_invitation(org_dictionary['id'])
        new_invitation = InvitationService.create_invitation(invitation_info, User(user), '').as_dict()
        invitation = InvitationService.find_invitation_by_id(new_invitation['id']).as_dict()
        assert invitation
        assert invitation['recipient_email'] == invitation_info['recipientEmail']


def test_find_invitation_by_id_exception(session, auth_mock):  # pylint:disable=unused-argument
    """Find an existing invitation with the provided id with exception."""
    invitation = InvitationService.find_invitation_by_id(None)
    assert invitation is None


def test_delete_invitation(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Delete the specified invitation."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
        org_dictionary = org.as_dict()
        invitation_info = factory_invitation(org_dictionary['id'])
        new_invitation = InvitationService.create_invitation(invitation_info, User(user), '').as_dict()
        InvitationService.delete_invitation(new_invitation['id'])
        invitation = InvitationService.find_invitation_by_id(new_invitation['id'])
        assert invitation is None


def test_delete_invitation_exception(session, auth_mock):  # pylint:disable=unused-argument
    """Delete the specified invitation with exception."""
    with pytest.raises(BusinessException) as exception:
        InvitationService.delete_invitation(None)

    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_update_invitation(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Update the specified invitation with new data."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
        org_dictionary = org.as_dict()
        invitation_info = factory_invitation(org_dictionary['id'])
        new_invitation = InvitationService.create_invitation(invitation_info, User(user), '')
        updated_invitation = new_invitation.update_invitation(User(user), '').as_dict()
        assert updated_invitation['status'] == 'PENDING'


def test_update_invitation_verify_different_tokens(session, auth_mock, keycloak_mock,  # pylint:disable=unused-argument
                                                   monkeypatch):
    """Update the specified invitation with new data."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
        org_dictionary = org.as_dict()
        invitation_info = factory_invitation(org_dictionary['id'])
        new_invitation = InvitationService.create_invitation(invitation_info, User(user), '')
        old_token = new_invitation.as_dict().get('token')
        with freeze_time(
                lambda: datetime.now() + timedelta(seconds=1)):  # to give time difference..or else token will be same..
            updated_invitation = new_invitation.update_invitation(User(user), '').as_dict()
            new_token = updated_invitation.get('token')
        assert old_token != new_token
        assert updated_invitation['status'] == 'PENDING'


def test_generate_confirmation_token(session):  # pylint:disable=unused-argument
    """Generate the invitation token."""
    confirmation_token = InvitationService.generate_confirmation_token(1)
    assert confirmation_token is not None


def test_validate_token_valid(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Validate the invitation token."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
        org_dictionary = org.as_dict()
        invitation_info = factory_invitation(org_dictionary['id'])
        new_invitation = InvitationService.create_invitation(invitation_info, User(user), '').as_dict()
        confirmation_token = InvitationService.generate_confirmation_token(new_invitation['id'])
        invitation_id = InvitationService.validate_token(confirmation_token).as_dict().get('id')
        assert invitation_id == new_invitation['id']


def test_validate_token_accepted(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Validate invalid invitation token."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
        org_dictionary = org.as_dict()
        user_invitee = factory_user_model(TestUserInfo.user1)
        invitation_info = factory_invitation(org_dictionary['id'])
        new_invitation = InvitationService.create_invitation(invitation_info, User(user_invitee), '').as_dict()
        confirmation_token = InvitationService.generate_confirmation_token(new_invitation['id'])
        InvitationService.accept_invitation(new_invitation['id'], User(user_invitee), '')

        with pytest.raises(BusinessException) as exception:
            InvitationService.validate_token(confirmation_token)

        assert exception.value.code == Error.ACTIONED_INVITATION.name


def test_validate_token_exception(session):  # pylint:disable=unused-argument
    """Validate the invitation token with exception."""
    with pytest.raises(BusinessException) as exception:
        InvitationService.validate_token(None)

    assert exception.value.code == Error.EXPIRED_INVITATION.name


def test_accept_invitation(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Accept the invitation and add membership from the invitation to the org."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        with patch.object(auth, 'check_auth', return_value=True):
            with patch.object(InvitationService, 'notify_admin', return_value=None):
                user_with_token = TestUserInfo.user_test
                user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
                user = factory_user_model(user_with_token)
                patch_token_info({'sub': user.keycloak_guid}, monkeypatch)

                org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
                org_dictionary = org.as_dict()
                invitation_info = factory_invitation(org_dictionary['id'])
                user_with_token_invitee = TestUserInfo.user1
                user_with_token_invitee['keycloak_guid'] = TestJwtClaims.edit_role_2['sub']
                user_invitee = factory_user_model(user_with_token_invitee)
                new_invitation = InvitationService.create_invitation(invitation_info, User(user_invitee), '')
                new_invitation_dict = new_invitation.as_dict()
                InvitationService.accept_invitation(new_invitation_dict['id'], User(user_invitee), '')
                patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
                members = MembershipService.get_members_for_org(org_dictionary['id'],
                                                                'PENDING_APPROVAL')
                assert members
                assert len(members) == 1


def test_accept_invitation_for_govm(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Accept the invitation and add membership from the invitation to the org."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        with patch.object(auth, 'check_auth', return_value=True):
            with patch.object(InvitationService, 'notify_admin', return_value=None):
                user_with_token = TestUserInfo.user_staff_admin
                user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
                user = factory_user_model(user_with_token)

                patch_token_info(TestJwtClaims.staff_admin_role, monkeypatch)

                org = OrgService.create_org(TestOrgInfo.org_govm, user_id=user.id)
                org_dictionary = org.as_dict()
                invitation_info = factory_invitation(org_dictionary['id'])
                user_with_token_invitee = TestUserInfo.user1
                user_with_token_invitee['keycloak_guid'] = TestJwtClaims.edit_role_2['sub']
                user_invitee = factory_user_model(user_with_token_invitee)
                new_invitation = InvitationService.create_invitation(invitation_info, User(user_invitee), '')
                new_invitation_dict = new_invitation.as_dict()
                with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
                    InvitationService.accept_invitation(new_invitation_dict['id'], User(user_invitee), '')
                    mock_alp.assert_called_with(Activity(action=ActivityAction.APPROVE_TEAM_MEMBER.value,
                                                org_id=ANY, name=ANY, id=ANY,
                                                value=ANY))

                members = MembershipService.get_members_for_org(org_dictionary['id'], 'ACTIVE')
                assert members
                assert len(members) == 1, 'user gets active membership'


def test_accept_invitation_exceptions(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Accept the invitation and add membership from the invitation to the org."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        with patch.object(auth, 'check_auth', return_value=True):
            with patch.object(InvitationService, 'notify_admin', return_value=None):
                user = factory_user_model(TestUserInfo.user_test)
                patch_token_info({'sub': user.keycloak_guid}, monkeypatch)
                org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
                org_dictionary = org.as_dict()
                invitation_info = factory_invitation(org_dictionary['id'])

                user_invitee = factory_user_model(TestUserInfo.user1)

                with pytest.raises(BusinessException) as exception:
                    InvitationService.accept_invitation(None, User(user_invitee), '')

                assert exception.value.code == Error.DATA_NOT_FOUND.name

                new_invitation = InvitationService.create_invitation(invitation_info, User(user_invitee), '')
                new_invitation_dict = new_invitation.as_dict()
                InvitationService.accept_invitation(new_invitation_dict['id'], User(user_invitee), '')

                with pytest.raises(BusinessException) as exception:
                    InvitationService.accept_invitation(new_invitation_dict['id'], User(user_invitee), '')

                assert exception.value.code == Error.ACTIONED_INVITATION.name

                with pytest.raises(BusinessException) as exception:
                    expired_invitation: InvitationModel = InvitationModel \
                        .find_invitation_by_id(new_invitation_dict['id'])
                    expired_invitation.invitation_status = InvitationStatusModel.get_status_by_code('EXPIRED')
                    expired_invitation.save()
                    InvitationService.accept_invitation(expired_invitation.id, User(user_invitee), '')

                assert exception.value.code == Error.EXPIRED_INVITATION.name


def test_get_invitations_by_org_id(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Find an existing invitation with the provided org id."""
    with patch.object(InvitationService, 'send_invitation', return_value=None):
        patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
        user_with_token = TestUserInfo.user_test
        user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
        user = factory_user_model(user_with_token)
        patch_token_info({'sub': user.keycloak_guid}, monkeypatch)
        org = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
        org_dictionary = org.as_dict()
        org_id = org_dictionary['id']
        invitation_info = factory_invitation(org_dictionary['id'])
        InvitationService.create_invitation(invitation_info, User(user), '').as_dict()
        invitations: list = InvitationService.get_invitations_for_org(org_id,
                                                                      status='PENDING',
                                                                      token_info=TestJwtClaims.public_user_role)
        assert invitations
        assert len(invitations) == 1

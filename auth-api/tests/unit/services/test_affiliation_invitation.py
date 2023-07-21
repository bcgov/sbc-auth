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
"""Tests for the Affiliation Invitation service.

Test suite to ensure that the Affiliation Invitation service routines are working as expected.
"""
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from freezegun import freeze_time

import auth_api.services.authorization as auth
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import AffiliationInvitation as AffiliationInvitationModel
from auth_api.models import InvitationStatus as InvitationStatusModel
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import AffiliationInvitation as AffiliationInvitationService
from auth_api.services import Entity as EntityService
from auth_api.services import Org as OrgService
from auth_api.services import User
from tests.utilities.factory_scenarios import TestEntityInfo, TestJwtClaims, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import factory_affiliation_invitation, factory_user_model, patch_token_info


def create_test_entity():
    """Create test entity data."""
    return EntityService.save_entity({
        'businessIdentifier': TestEntityInfo.entity_passcode['businessIdentifier'],
        'businessNumber': TestEntityInfo.entity_passcode['businessNumber'],
        'passCode': TestEntityInfo.entity_passcode['passCode'],
        'name': TestEntityInfo.entity_passcode['name'],
        'corpTypeCode': TestEntityInfo.entity_passcode['corpTypeCode']
    })


def setup_org_and_entity(user):
    """Create test org and entity data."""
    from_org = OrgService.create_org(TestOrgInfo.affiliation_from_org, user_id=user.id)
    to_org = OrgService.create_org(TestOrgInfo.affiliation_to_org, user_id=user.id)
    entity = create_test_entity()
    from_org_dictionary = from_org.as_dict()
    to_org_dictionary = to_org.as_dict()
    entity_dictionary = entity.as_dict()

    return from_org_dictionary, to_org_dictionary, entity_dictionary


def test_as_dict(session, auth_mock, keycloak_mock, business_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that the Affiliation Invitation is exported correctly as a dictionary."""
    with patch.object(AffiliationInvitationService, 'send_affiliation_invitation', return_value=None):
        user = factory_user_model()
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)

        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary['id'],
            to_org_id=to_org_dictionary['id'],
            business_identifier=entity_dictionary['business_identifier'])

        affiliation_invitation = AffiliationInvitationService.create_affiliation_invitation(affiliation_invitation_info,
                                                                                            User(user), '')
        affiliation_invitation_dictionary = affiliation_invitation.as_dict()
        assert affiliation_invitation_dictionary['recipient_email'] == affiliation_invitation_info['recipientEmail']


def test_create_affiliation_invitation(session, auth_mock, keycloak_mock, business_mock,
                                       monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Affiliation Invitation can be created."""
    with patch.object(AffiliationInvitationService, 'send_affiliation_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)

        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary['id'],
            to_org_id=to_org_dictionary['id'],
            business_identifier=entity_dictionary['business_identifier'])

        affiliation_invitation = AffiliationInvitationService.create_affiliation_invitation(affiliation_invitation_info,
                                                                                            User(user), '')
        invitation_dictionary = affiliation_invitation.as_dict()
        assert invitation_dictionary['recipient_email'] == affiliation_invitation_info['recipientEmail']
        assert invitation_dictionary['id']


def test_find_affiliation_invitation_by_id(session, auth_mock, keycloak_mock, business_mock,
                                           monkeypatch):  # pylint:disable=unused-argument
    """Find an existing affiliation invitation with the provided id."""
    with patch.object(AffiliationInvitationService, 'send_affiliation_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)

        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary['id'],
            to_org_id=to_org_dictionary['id'],
            business_identifier=entity_dictionary['business_identifier'])

        new_invitation = AffiliationInvitationService.create_affiliation_invitation(affiliation_invitation_info,
                                                                                    User(user), '').as_dict()
        invitation = AffiliationInvitationService.find_affiliation_invitation_by_id(new_invitation['id']).as_dict()

        assert invitation
        assert invitation['recipient_email'] == affiliation_invitation_info['recipientEmail']


def test_find_invitation_by_id_exception(session, auth_mock):  # pylint:disable=unused-argument
    """Find an existing affiliation invitation with the provided id with exception."""
    affiliation_invitation = AffiliationInvitationService.find_affiliation_invitation_by_id(None)
    assert affiliation_invitation is None


def test_delete_affiliation_invitation(session, auth_mock, keycloak_mock, business_mock,
                                       monkeypatch):  # pylint:disable=unused-argument
    """Delete the specified affiliation invitation."""
    with patch.object(AffiliationInvitationService, 'send_affiliation_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary['id'],
            to_org_id=to_org_dictionary['id'],
            business_identifier=entity_dictionary['business_identifier'])

        new_invitation = AffiliationInvitationService.create_affiliation_invitation(affiliation_invitation_info,
                                                                                    User(user), '').as_dict()
        AffiliationInvitationService.delete_affiliation_invitation(new_invitation['id'])
        invitation = AffiliationInvitationService.find_affiliation_invitation_by_id(new_invitation['id'])
        assert invitation is None


def test_delete_affiliation_invitation_exception(session, auth_mock):  # pylint:disable=unused-argument
    """Delete the specified affiliation invitation with exception."""
    with pytest.raises(BusinessException) as exception:
        AffiliationInvitationService.delete_affiliation_invitation(None)

    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_update_affiliation_invitation(session, auth_mock, keycloak_mock, business_mock,
                                       monkeypatch):  # pylint:disable=unused-argument
    """Update the specified affiliation invitation with new data."""
    with patch.object(AffiliationInvitationService, 'send_affiliation_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary['id'],
            to_org_id=to_org_dictionary['id'],
            business_identifier=entity_dictionary['business_identifier'])

        new_invitation = AffiliationInvitationService.create_affiliation_invitation(affiliation_invitation_info,
                                                                                    User(user), '')
        updated_invitation = new_invitation.update_affiliation_invitation(User(user), '', {}).as_dict()
        assert updated_invitation['status'] == 'PENDING'


def test_update_invitation_verify_different_tokens(session, auth_mock, keycloak_mock,
                                                   business_mock, monkeypatch):  # pylint:disable=unused-argument
    """Update the specified affiliation invitation to check for token difference."""
    with patch.object(AffiliationInvitationService, 'send_affiliation_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary['id'],
            to_org_id=to_org_dictionary['id'],
            business_identifier=entity_dictionary['business_identifier'])

        new_invitation = AffiliationInvitationService.create_affiliation_invitation(affiliation_invitation_info,
                                                                                    User(user), '')
        old_token = new_invitation.as_dict().get('token')
        with freeze_time(
                lambda: datetime.now() + timedelta(seconds=1)):  # to give time difference..or else token will be same..
            updated_invitation = new_invitation.update_affiliation_invitation(User(user), '', {}).as_dict()
            new_token = updated_invitation.get('token')
        assert old_token != new_token
        assert updated_invitation['status'] == 'PENDING'


def test_generate_confirmation_token(session):  # pylint:disable=unused-argument
    """Generate the affiliation invitation token."""
    confirmation_token = AffiliationInvitationService.generate_confirmation_token(1, 2, 3, 'CP1234567')
    assert confirmation_token is not None


def test_validate_token_accepted(session, auth_mock, keycloak_mock, business_mock,
                                 monkeypatch):  # pylint:disable=unused-argument
    """Validate invalid invitation token."""
    with patch.object(AffiliationInvitationService, 'send_affiliation_invitation', return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        user_invitee = factory_user_model(TestUserInfo.user1)
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary['id'],
            to_org_id=to_org_dictionary['id'],
            business_identifier=entity_dictionary['business_identifier'])

        new_invitation = AffiliationInvitationService.create_affiliation_invitation(affiliation_invitation_info,
                                                                                    User(user_invitee), '').as_dict()
        token = AffiliationInvitationService\
            .generate_confirmation_token(new_invitation['id'],
                                         new_invitation['from_org']['id'],
                                         new_invitation['to_org']['id'],
                                         entity_dictionary['business_identifier'])

        AffiliationInvitationService.accept_affiliation_invitation(new_invitation['id'], User(user_invitee), '')

        with pytest.raises(BusinessException) as exception:
            AffiliationInvitationService.validate_token(token, new_invitation['id'])

        assert exception.value.code == Error.ACTIONED_AFFILIATION_INVITATION.name


def test_validate_token_exception(session):  # pylint:disable=unused-argument
    """Validate the affiliation invitation token with exception."""
    with pytest.raises(BusinessException) as exception:
        AffiliationInvitationService.validate_token(None, 1)

    assert exception.value.code == Error.EXPIRED_AFFILIATION_INVITATION.name


def test_accept_affiliation_invitation(session, auth_mock, keycloak_mock, business_mock,
                                       monkeypatch):  # pylint:disable=unused-argument
    """Accept the affiliation invitation and add the affiliation from the invitation."""
    with patch.object(AffiliationInvitationService, 'send_affiliation_invitation', return_value=None):
        with patch.object(auth, 'check_auth', return_value=True):
            user_with_token = TestUserInfo.user_test
            user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
            user_with_token['idp_userid'] = TestJwtClaims.public_user_role['idp_userid']
            user = factory_user_model(user_with_token)
            patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)

            from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

            affiliation_invitation_info = factory_affiliation_invitation(
                from_org_id=from_org_dictionary['id'],
                to_org_id=to_org_dictionary['id'],
                business_identifier=entity_dictionary['business_identifier'])

            user_with_token_invitee = TestUserInfo.user1
            user_with_token_invitee['keycloak_guid'] = TestJwtClaims.edit_role_2['sub']
            user_invitee = factory_user_model(user_with_token_invitee)

            new_invitation = AffiliationInvitationService \
                .create_affiliation_invitation(affiliation_invitation_info,
                                               User(user_invitee), '').as_dict()

            invitation = AffiliationInvitationService.accept_affiliation_invitation(new_invitation['id'],
                                                                                    User(user_invitee),
                                                                                    '').as_dict()
            patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
            affiliation = AffiliationService.find_affiliation(new_invitation['to_org']['id'],
                                                              entity_dictionary['business_identifier'])
            assert affiliation
            assert invitation
            assert affiliation['id'] == invitation['affiliation_id']


def test_accept_invitation_exceptions(session, auth_mock, keycloak_mock, business_mock,
                                      monkeypatch):  # pylint:disable=unused-argument
    """Accept the affiliation invitation exceptions."""
    with patch.object(AffiliationInvitationService, 'send_affiliation_invitation', return_value=None):
        with patch.object(auth, 'check_auth', return_value=True):
            user = factory_user_model(TestUserInfo.user_test)
            patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
            from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

            affiliation_invitation_info = factory_affiliation_invitation(
                from_org_id=from_org_dictionary['id'],
                to_org_id=to_org_dictionary['id'],
                business_identifier=entity_dictionary['business_identifier'])

            user_invitee = factory_user_model(TestUserInfo.user1)

            # Accepting a non-existent invitation should raise not found exception
            with pytest.raises(BusinessException) as exception:
                AffiliationInvitationService.accept_affiliation_invitation(None, User(user_invitee), '')

            assert exception.value.code == Error.DATA_NOT_FOUND.name

            # Accepting an invitation multiple times should raise actioned invitation exception
            new_invitation = AffiliationInvitationService \
                .create_affiliation_invitation(affiliation_invitation_info,
                                               User(user_invitee), '').as_dict()

            AffiliationInvitationService.accept_affiliation_invitation(new_invitation['id'], User(user_invitee), '')

            with pytest.raises(BusinessException) as exception:
                AffiliationInvitationService.accept_affiliation_invitation(new_invitation['id'],
                                                                           User(user_invitee), '')

            assert exception.value.code == Error.ACTIONED_AFFILIATION_INVITATION.name

            # Accepting an expired invitation should raise an expired invitation exception
            with pytest.raises(BusinessException) as exception:
                expired_invitation: AffiliationInvitationModel = AffiliationInvitationModel \
                    .find_invitation_by_id(new_invitation['id'])
                expired_invitation.invitation_status = InvitationStatusModel.get_status_by_code('EXPIRED')
                expired_invitation.save()
                AffiliationInvitationService.accept_affiliation_invitation(expired_invitation.id,
                                                                           User(user_invitee),
                                                                           '')
            assert exception.value.code == Error.EXPIRED_AFFILIATION_INVITATION.name


def test_get_invitations_by_from_org_id(session, auth_mock, keycloak_mock, business_mock,
                                        monkeypatch):  # pylint:disable=unused-argument
    """Find an existing invitation with the provided from org id."""
    with patch.object(AffiliationInvitationService, 'send_affiliation_invitation', return_value=None):
        patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
        user_with_token = TestUserInfo.user_test
        user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
        user = factory_user_model(user_with_token)
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        from_org_id = from_org_dictionary['id']
        to_org_id = to_org_dictionary['id']
        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_id,
            to_org_id=to_org_id,
            business_identifier=entity_dictionary['business_identifier'])

        AffiliationInvitationService.create_affiliation_invitation(affiliation_invitation_info, User(user), '')

        invitations: list = AffiliationInvitationService\
            .get_invitations_for_from_org(org_id=from_org_id,
                                          status='PENDING',
                                          token_info=TestJwtClaims.public_user_role)
        assert invitations
        assert len(invitations) == 1


def test_get_invitations_by_to_org_id(session, auth_mock, keycloak_mock, business_mock,
                                      monkeypatch):  # pylint:disable=unused-argument
    """Find an existing invitation with the provided to org id."""
    with patch.object(AffiliationInvitationService, 'send_affiliation_invitation', return_value=None):
        patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
        user_with_token = TestUserInfo.user_test
        user_with_token['keycloak_guid'] = TestJwtClaims.public_user_role['sub']
        user = factory_user_model(user_with_token)
        patch_token_info({'sub': user.keycloak_guid, 'idp_userid': user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        from_org_id = from_org_dictionary['id']
        to_org_id = to_org_dictionary['id']
        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_id,
            to_org_id=to_org_id,
            business_identifier=entity_dictionary['business_identifier'])

        AffiliationInvitationService.create_affiliation_invitation(affiliation_invitation_info, User(user), '')

        invitations: list = AffiliationInvitationService \
            .get_invitations_for_to_org(org_id=to_org_id, status='PENDING', token_info=TestJwtClaims.public_user_role)
        assert invitations
        assert len(invitations) == 1

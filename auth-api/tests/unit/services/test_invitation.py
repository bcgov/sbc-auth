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

import pytest

from auth_api.models import User as UserModel
from auth_api.services import Invitation as InvitationService
from auth_api.services import Org as OrgService
from auth_api.services import notification as NotificationService
from unittest.mock import patch


TEST_ORG_INFO = {
    'name': 'My Test Org'
}

TEST_UPDATED_INVITATION_INFO = {
    'status': 'ACCEPTED'
}

def factory_user_model(username,
                       firstname=None,
                       lastname=None,
                       roles=None,
                       keycloak_guid=None):
    """Return a valid user object stamped with the supplied designation."""
    user = UserModel(username=username,
                     firstname=firstname,
                     lastname=lastname,
                     roles=roles,
                     keycloak_guid=keycloak_guid)
    user.save()
    return user


def test_as_dict(session):  # pylint:disable=unused-argument
    """Assert that the Invitation is exported correctly as a dictionary."""
    user = factory_user_model(username='testuser',
                              roles='{edit,uma_authorization,basic}',
                              keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    org = OrgService.create_org(TEST_ORG_INFO, user_id=user.id)
    org_dictionary = org.as_dict()
    print(org_dictionary)
    invitation_info = {
        'recipientEmail': 'abc.test@gmail.com',
        'sentDate': '2019-09-09',
        'membership': [
            {
                'membershipType': 'MEMBER',
                'orgId': org_dictionary['id']
            }
        ]
    }
    invitation = InvitationService.create_invitation(invitation_info, user.id)
    invitation_dictionary = invitation.as_dict()
    assert invitation_dictionary['recipientEmail'] == invitation_info['recipientEmail']


def test_create_invitation(session):  # pylint:disable=unused-argument
    """Assert that an Org can be created."""
    with patch.object(NotificationService.Notification, 'send_email', return_value=None) as mock_notify:
        user = factory_user_model(username='testuser',
                                  roles='{edit,uma_authorization,basic}',
                                  keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
        org = OrgService.create_org(TEST_ORG_INFO, user_id=user.id)
        org_dictionary = org.as_dict()
        invitation_info = {
            'recipientEmail': 'abc.test@gmail.com',
            'sentDate': '2019-09-09',
            'membership': [
                {
                    'membershipType': 'MEMBER',
                    'orgId':  org_dictionary['id']
                }
            ]
        }
        invitation = InvitationService.create_invitation(invitation_info, user.id)
        invitation_dictionary = invitation.as_dict()
        assert invitation_dictionary['recipientEmail'] == invitation_info['recipientEmail']
        assert invitation_dictionary['id']
        mock_notify.assert_called()


def test_get_invitations(session):
    user = factory_user_model(username='testuser',
                              roles='{edit,uma_authorization,basic}',
                              keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    org = OrgService.create_org(TEST_ORG_INFO, user_id=user.id)
    org_dictionary = org.as_dict()
    invitation_info = {
        'recipientEmail': 'abc.test@gmail.com',
        'sentDate': '2019-09-09',
        'membership': [
            {
                'membershipType': 'MEMBER',
                'orgId': org_dictionary['id']
            }
        ]
    }
    InvitationService.create_invitation(invitation_info, user.id)
    invitation = InvitationService.get_invitations(user.id)
    invitation_dictionary = invitation[0]
    assert invitation_dictionary['recipientEmail'] == invitation_info['recipientEmail']


def test_find_invitation_by_id(session):
    """Find an existing invitation with the provided id."""
    user = factory_user_model(username='testuser',
                              roles='{edit,uma_authorization,basic}',
                              keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    org = OrgService.create_org(TEST_ORG_INFO, user_id=user.id)
    org_dictionary = org.as_dict()
    invitation_info = {
        'recipientEmail': 'abc.test@gmail.com',
        'sentDate': '2019-09-09',
        'membership': [
            {
                'membershipType': 'MEMBER',
                'orgId': org_dictionary['id']
            }
        ]
    }
    new_invitation = InvitationService.create_invitation(invitation_info, user.id).as_dict()
    invitation = InvitationService.find_invitation_by_id(new_invitation['id']).as_dict()
    assert invitation
    assert invitation['recipientEmail'] == invitation_info['recipientEmail']


def test_delete_invitation(session):
    """Delete the specified invitation."""
    user = factory_user_model(username='testuser',
                              roles='{edit,uma_authorization,basic}',
                              keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    org = OrgService.create_org(TEST_ORG_INFO, user_id=user.id)
    org_dictionary = org.as_dict()
    invitation_info = {
        'recipientEmail': 'abc.test@gmail.com',
        'sentDate': '2019-09-09',
        'membership': [
            {
                'membershipType': 'MEMBER',
                'orgId': org_dictionary['id']
            }
        ]
    }
    new_invitation = InvitationService.create_invitation(invitation_info, user.id).as_dict()
    InvitationService.delete_invitation(new_invitation['id'])
    invitation = InvitationService.find_invitation_by_id(new_invitation['id'])
    assert invitation is None


def test_update_invitation(session):
    """Update the specified invitation with new data."""
    user = factory_user_model(username='testuser',
                              roles='{edit,uma_authorization,basic}',
                              keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    org = OrgService.create_org(TEST_ORG_INFO, user_id=user.id)
    org_dictionary = org.as_dict()
    invitation_info = {
        'recipientEmail': 'abc.test@gmail.com',
        'sentDate': '2019-09-09',
        'membership': [
            {
                'membershipType': 'MEMBER',
                'orgId': org_dictionary['id']
            }
        ]
    }
    new_invitation = InvitationService.create_invitation(invitation_info, user.id)
    new_invitation_dict = new_invitation.as_dict()
    updated_invitation_info = {
            "id": new_invitation_dict['id'],
            "sentDate": "2019-09-09T00:00:00+00:00",
            "status": "ACCEPTED",
            "acceptedDate": "2019-09-11T00:00:00+00:00"
    }
    updated_invitation = new_invitation.update_invitation(updated_invitation_info).as_dict()
    assert updated_invitation['status'] == updated_invitation_info['status']

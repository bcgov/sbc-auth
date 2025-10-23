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
"""Tests for the Invitation model.

Test suite to ensure that the  model routines are working as expected.
"""

from _datetime import datetime, timedelta

from auth_api.config import get_named_config
from auth_api.models import Invitation as InvitationModel
from auth_api.models import InvitationMembership as InvitationMembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.models import PaymentType as PaymentTypeModel
from auth_api.models import User


def factory_invitation_model(session, status, sent_date=datetime.now()):
    """Produce a templated invitation model."""
    user = User(username="CP1234567", keycloak_guid="1b20db59-19a0-4727-affe-c6f64309fd04")

    session.add(user)
    session.commit()

    org_type = OrgTypeModel(code="TEST", description="Test")
    session.add(org_type)
    session.commit()

    org_status = OrgStatusModel(code="TEST", description="Test")
    session.add(org_status)
    session.commit()

    preferred_payment = PaymentTypeModel(code="TEST", description="Test")
    session.add(preferred_payment)
    session.commit()

    org = OrgModel()
    org.name = "Test Org"
    org.org_type = org_type
    org.org_status = org_status
    org.preferred_payment = preferred_payment
    org.save()

    invitation = InvitationModel()
    invitation.recipient_email = "abc@test.com"
    invitation.sender = user
    invitation.sent_date = sent_date
    invitation.invitation_status_code = status
    invitation.token = "ABCD"  # noqa: S105

    invitation_membership = InvitationMembershipModel()
    invitation_membership.org_id = org.id
    invitation_membership.membership_type_code = "USER"
    invitation.membership.append(invitation_membership)

    invitation.save()
    return invitation


def test_create_invitation(session):
    """Assert that an Invitation can be stored in the service."""
    invitation = factory_invitation_model(session=session, status="PENDING")
    session.add(invitation)
    session.commit()
    assert invitation.id is not None


def test_find_invitation_by_id(session):  # pylint:disable=unused-argument
    """Assert that an Invitation can retrieved by its id."""
    invitation = factory_invitation_model(session=session, status="PENDING")
    session.add(invitation)
    session.commit()

    retrieved_invitation = InvitationModel.find_invitation_by_id(invitation.id)
    assert retrieved_invitation
    assert retrieved_invitation.id == invitation.id


def test_find_invitations_by_user(session):  # pylint:disable=unused-argument
    """Assert that an Invitation can retrieved by the user id."""
    invitation = factory_invitation_model(session=session, status="PENDING")
    session.add(invitation)
    session.commit()

    retrieved_invitation = InvitationModel.find_invitations_by_user(invitation.sender_id)
    assert len(retrieved_invitation) > 0
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email
    assert retrieved_invitation[0].token == invitation.token


def test_update_invitation_as_retried(session):  # pylint:disable=unused-argument
    """Assert that an Invitation can be updated."""
    invitation = factory_invitation_model(session=session, status="FAILED")
    session.add(invitation)
    session.commit()
    invitation.update_invitation_as_retried()
    assert invitation
    assert invitation.invitation_status_code == "PENDING"


def test_find_invitations_by_org(session):  # pylint:disable=unused-argument
    """Assert that Invitations for a specified org can be retrieved."""
    invitation = factory_invitation_model(session=session, status="PENDING")
    session.add(invitation)
    session.commit()

    found_invitations = InvitationModel.find_invitations_by_org(invitation.membership[0].org_id)
    assert found_invitations
    assert len(found_invitations) == 1
    assert found_invitations[0].membership[0].org_id == invitation.membership[0].org_id
    assert invitation.invitation_status_code == "PENDING"


def test_find_pending_invitations_by_user(session):  # pylint:disable=unused-argument
    """Assert that an Invitation can retrieved by the user id."""
    invitation = factory_invitation_model(session=session, status="PENDING")
    session.add(invitation)
    session.commit()

    retrieved_invitation = InvitationModel.find_pending_invitations_by_user(invitation.sender_id)
    assert len(retrieved_invitation) == 1
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email


def test_find_pending_invitations_by_org(session):  # pylint:disable=unused-argument
    """Assert that an Invitation can retrieved by the org id."""
    invitation = factory_invitation_model(session=session, status="PENDING")
    session.add(invitation)
    session.commit()

    retrieved_invitation = InvitationModel.find_pending_invitations_by_org(invitation.membership[0].org_id)
    assert len(retrieved_invitation) == 1
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email


def test_invitations_by_status(session):  # pylint:disable=unused-argument
    """Assert that an Invitation can retrieved by the user id."""
    invitation = factory_invitation_model(session=session, status="PENDING")
    session.add(invitation)
    session.commit()

    retrieved_invitation = InvitationModel.find_invitations_by_status(invitation.sender_id, "FAILED")
    assert len(retrieved_invitation) == 0


def test_create_from_dict(session):  # pylint:disable=unused-argument
    """Assert that an Entity can be created from schema."""
    user = User(username="CP1234567", keycloak_guid="1b20db59-19a0-4727-affe-c6f64309fd04")

    session.add(user)
    session.commit()

    org_type = OrgTypeModel(code="TEST", description="Test")
    session.add(org_type)
    session.commit()

    org_status = OrgStatusModel(code="TEST", description="Test")
    session.add(org_status)
    session.commit()

    preferred_payment = PaymentTypeModel(code="TEST", description="Test")
    session.add(preferred_payment)
    session.commit()

    org = OrgModel()
    org.name = "Test Org"
    org.org_type = org_type
    org.org_status = org_status
    org.preferred_payment = preferred_payment
    org.save()

    invitation_info = {
        "recipientEmail": "abc.test@gmail.com",
        "membership": [{"membershipType": "USER", "orgId": org.id}],
    }
    result_invitation = InvitationModel.create_from_dict(invitation_info, user.id, "STANDARD")

    assert result_invitation.id is not None


def test_create_from_dict_no_schema(session):  # pylint:disable=unused-argument
    """Assert that an Entity can not be created without schema."""
    user = User(username="CP1234567", keycloak_guid="1b20db59-19a0-4727-affe-c6f64309fd04")

    session.add(user)
    session.commit()

    result_invitation = InvitationModel.create_from_dict(None, user.id, "STANDARD")

    assert result_invitation is None


def test_invitations_status_expiry(session):  # pylint:disable=unused-argument
    """Assert can set the status from PENDING to EXPIRED."""
    sent_date = datetime.now() - timedelta(days=int(get_named_config().TOKEN_EXPIRY_PERIOD) + 1)
    invitation = factory_invitation_model(session=session, status="PENDING", sent_date=sent_date)
    session.add(invitation)
    session.commit()

    result: str = invitation.status

    assert result == "EXPIRED"

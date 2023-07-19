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
from auth_api.models import AffiliationInvitation as AffiliationInvitationModel
from auth_api.models import Entity as EntityModel
from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.models import PaymentType as PaymentTypeModel
from auth_api.models import User


def factory_affiliation_invitation_model(session, status, sent_date=datetime.now()):
    """Produce a templated affiliation_invitation model."""
    user = User(username='CP1234567',
                keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    session.add(user)
    session.commit()

    org_type = OrgTypeModel(code='TEST', description='Test')
    session.add(org_type)
    session.commit()

    org_status = OrgStatusModel(code='TEST', description='Test')
    session.add(org_status)
    session.commit()

    preferred_payment = PaymentTypeModel(code='TEST', description='Test')
    session.add(preferred_payment)
    session.commit()

    from_org = OrgModel()
    from_org.name = 'Test From Org'
    from_org.org_type = org_type
    from_org.org_status = org_status
    from_org.preferred_payment = preferred_payment
    from_org.save()

    to_org = OrgModel()
    to_org.name = 'Test To Org'
    to_org.org_type = org_type
    to_org.org_status = org_status
    to_org.preferred_payment = preferred_payment
    to_org.save()

    entity = EntityModel(business_identifier='CP1234567', business_number='791861073BC0001', name='Interesting, Inc.',
                         corp_type_code='CP')
    entity.save()

    affiliation_invitation = AffiliationInvitationModel()
    affiliation_invitation.recipient_email = 'abc@test.com'
    affiliation_invitation.sender = user
    affiliation_invitation.sent_date = sent_date
    affiliation_invitation.invitation_status_code = status
    affiliation_invitation.token = 'ABCD'
    affiliation_invitation.from_org_id = from_org.id
    affiliation_invitation.to_org_id = to_org.id
    affiliation_invitation.entity_id = entity.id

    affiliation_invitation.save()
    return affiliation_invitation


def test_create_affiliation_invitation(session):
    """Assert that an Affiliation Invitation can be stored in the service."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()
    assert invitation.id is not None


def test_find_invitation_by_id(session):
    """Assert that an Affiliation Invitation can be retrieved by its id."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()

    retrieved_invitation = AffiliationInvitationModel.find_invitation_by_id(invitation.id)
    assert retrieved_invitation
    assert retrieved_invitation.id == invitation.id


def test_find_invitations_by_sender(session):
    """Assert that an Affiliation Invitation sender can be retrieved by the user id."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()

    retrieved_invitation = AffiliationInvitationModel.find_invitations_by_sender(invitation.sender_id)
    assert len(retrieved_invitation) > 0
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email
    assert retrieved_invitation[0].token == invitation.token


def test_update_invitation_as_retried(session):
    """Assert that an Affiliation Invitation can be updated."""
    invitation = factory_affiliation_invitation_model(session=session, status='FAILED')
    session.add(invitation)
    session.commit()
    invitation.update_invitation_as_retried(invitation.sender.id)
    assert invitation
    assert invitation.invitation_status_code == 'PENDING'


def test_find_invitations_from_org(session):
    """Assert that Affiliation Invitations from a specified org can be retrieved."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()

    found_invitations = AffiliationInvitationModel.find_invitations_from_org(invitation.from_org_id)
    assert found_invitations
    assert len(found_invitations) == 1
    assert found_invitations[0].from_org_id == invitation.from_org_id
    assert invitation.invitation_status_code == 'PENDING'


def test_find_invitations_to_org(session):  # pylint:disable=unused-argument
    """Assert that Affiliation Invitations to a specified org can be retrieved."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()

    found_invitations = AffiliationInvitationModel.find_invitations_to_org(invitation.to_org_id)
    assert found_invitations
    assert len(found_invitations) == 1
    assert found_invitations[0].to_org_id == invitation.to_org_id
    assert invitation.invitation_status_code == 'PENDING'


def test_find_invitations_by_entity(session):  # pylint:disable=unused-argument
    """Assert that Affiliation Invitation for an entity can be retrieved."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()

    found_invitations = AffiliationInvitationModel.find_invitations_by_entity(invitation.entity_id)
    assert found_invitations
    assert len(found_invitations) == 1
    assert found_invitations[0].entity_id == invitation.entity_id
    assert invitation.invitation_status_code == 'PENDING'


def test_find_pending_invitations_by_sender(session):  # pylint:disable=unused-argument
    """Assert that pending Affiliation Invitations can be retrieved by the sender user id."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()

    retrieved_invitation = AffiliationInvitationModel.find_pending_invitations_by_sender(invitation.sender_id)
    assert len(retrieved_invitation) == 1
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email
    assert invitation.invitation_status_code == 'PENDING'


def test_find_pending_invitations_by_from_org(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation Invitation can be retrieved by the from org id."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()

    retrieved_invitation = AffiliationInvitationModel.find_pending_invitations_by_from_org(invitation.from_org_id)
    assert len(retrieved_invitation) == 1
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email
    assert invitation.invitation_status_code == 'PENDING'


def test_find_pending_invitations_by_to_org(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation Invitation can be retrieved by the to org id."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()

    retrieved_invitation = AffiliationInvitationModel.find_pending_invitations_by_to_org(invitation.to_org_id)
    assert len(retrieved_invitation) == 1
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email
    assert invitation.invitation_status_code == 'PENDING'


def test_invitations_by_status(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation Invitation can be retrieved by the status."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()

    retrieved_invitation = AffiliationInvitationModel.find_invitations_by_status(invitation.sender_id, 'PENDING')
    assert len(retrieved_invitation) >= 0

    retrieved_invitation = AffiliationInvitationModel.find_invitations_by_status(invitation.sender_id, 'INVALID')
    assert len(retrieved_invitation) == 0


def test_invitations_by_invalid_status(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation Invitations are not returned with an invalid status."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()

    retrieved_invitation = AffiliationInvitationModel.find_invitations_by_status(invitation.sender_id, 'INVALID')
    assert len(retrieved_invitation) == 0


def test_find_invitations_by_org_entity_ids(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation Invitation can be retrieved by the org and entity ids."""
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING')
    session.add(invitation)
    session.commit()

    retrieved_invitation = AffiliationInvitationModel.find_invitations_by_org_entity_ids(invitation.from_org_id,
                                                                                         invitation.to_org_id,
                                                                                         invitation.entity_id)
    assert len(retrieved_invitation) == 1
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email
    assert invitation.invitation_status_code == 'PENDING'


def test_create_from_dict(session):  # pylint:disable=unused-argument
    """Assert that an Entity can be created from schema."""
    user = User(username='CP1234567',
                keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    session.add(user)
    session.commit()

    org_type = OrgTypeModel(code='TEST', description='Test')
    session.add(org_type)
    session.commit()

    org_status = OrgStatusModel(code='TEST', description='Test')
    session.add(org_status)
    session.commit()

    preferred_payment = PaymentTypeModel(code='TEST', description='Test')
    session.add(preferred_payment)
    session.commit()

    from_org = OrgModel()
    from_org.name = 'Test From Org'
    from_org.org_type = org_type
    from_org.org_status = org_status
    from_org.preferred_payment = preferred_payment
    from_org.save()

    to_org = OrgModel()
    to_org.name = 'Test To Org'
    to_org.org_type = org_type
    to_org.org_status = org_status
    to_org.preferred_payment = preferred_payment
    to_org.save()

    entity = EntityModel(business_identifier='CP1234567', business_number='791861073BC0001', name='Interesting, Inc.',
                         corp_type_code='CP')
    entity.save()

    invitation_info = {
        'recipientEmail': 'abc.test@gmail.com',
        'fromOrgId': from_org.id,
        'toOrgId': to_org.id,
        'entityId': entity.id
    }
    result_invitation = AffiliationInvitationModel.create_from_dict(invitation_info, user.id)

    assert result_invitation.id is not None
    assert result_invitation.affiliation_id is None


def test_create_from_dict_no_schema(session):  # pylint:disable=unused-argument
    """Assert that an affiliation invitation can not be created without schema."""
    user = User(username='CP1234567',
                keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    session.add(user)
    session.commit()

    result_invitation = AffiliationInvitationModel.create_from_dict(None, user.id)

    assert result_invitation is None


def test_invitations_status_expiry(session):  # pylint:disable=unused-argument
    """Assert can set the status from PENDING to EXPIRED."""
    sent_date = datetime.now() - timedelta(days=int(get_named_config().TOKEN_EXPIRY_PERIOD) + 1)
    invitation = factory_affiliation_invitation_model(session=session, status='PENDING', sent_date=sent_date)
    session.add(invitation)
    session.commit()

    result: str = invitation.status

    assert result == 'EXPIRED'

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
"""Tests for the Invitation model.

Test suite to ensure that the  model routines are working as expected.
"""
from _datetime import datetime, timedelta
from typing import List
from uuid import uuid4

from auth_api.config import get_named_config
from auth_api.models import AffiliationInvitation as AffiliationInvitationModel
from auth_api.models import Entity as EntityModel
from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.models import PaymentType as PaymentTypeModel
from auth_api.models import User
from auth_api.models.dataclass import AffiliationInvitationSearch
from auth_api.utils.enums import AffiliationInvitationType, InvitationStatus


def _get_random_affiliation_invitation_model(
        # mandatory params
        user: User,
        from_org_id: int,
        to_org_id: int,
        entity_id: int,
        # optional params below
        affiliation_identifier: int = 1,
        affiliation_type='REQUEST',
        invitation_token='ABCD',
        sent_date=datetime.now(),
        recipient_email=None,
        invitation_status_code=InvitationStatus.PENDING.value,
        approver_id=None,
        additional_message=None
):
    if recipient_email is None:
        recipient_email = str(uuid4()) + '@test.com'

    affiliation_invitation_model = AffiliationInvitationModel()
    affiliation_invitation_model.recipient_email = recipient_email
    affiliation_invitation_model.sender = user
    affiliation_invitation_model.sent_date = sent_date
    affiliation_invitation_model.invitation_status_code = invitation_status_code
    affiliation_invitation_model.token = invitation_token
    affiliation_invitation_model.from_org_id = from_org_id
    affiliation_invitation_model.to_org_id = to_org_id
    affiliation_invitation_model.entity_id = entity_id
    affiliation_invitation_model.type = affiliation_type
    affiliation_invitation_model.approver_id = approver_id
    affiliation_invitation_model.additional_message = additional_message
    return affiliation_invitation_model


def _create_org(new_org_id, org_type: OrgTypeModel, org_status: OrgStatusModel, preferred_payment: PaymentTypeModel):
    random_org = OrgModel()
    random_org.name = f'Test Org #${new_org_id}'
    random_org.org_type = org_type
    random_org.org_status = org_status
    random_org.preferred_payment = preferred_payment
    random_org.id = new_org_id
    return random_org


def factory_affiliation_invitation_model(session, status, sent_date=datetime.now(),
                                         invitation_type: AffiliationInvitationType = None):
    """Produce a templated affiliation_invitation model."""
    user = User(username='CP1234567',
                keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    user.save()

    org_type = OrgTypeModel(code='TEST', description='Test')
    org_type.save()

    org_status = OrgStatusModel(code='TEST', description='Test')
    org_status.save()

    preferred_payment = PaymentTypeModel(code='TEST', description='Test')
    preferred_payment.save()

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
    if invitation_type is not None:
        affiliation_invitation.type = invitation_type

    affiliation_invitation.save()
    return affiliation_invitation


def test_create_affiliation_invitation(session):
    """Assert that an Affiliation Invitation can be stored in the service."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()
    assert invitation.id is not None


def test_find_invitation_by_id(session):
    """Assert that an Affiliation Invitation can be retrieved by its id."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()

    retrieved_invitation = AffiliationInvitationModel.find_invitation_by_id(invitation.id)
    assert retrieved_invitation
    assert retrieved_invitation.id == invitation.id


def test_find_invitations_by_sender(session):
    """Assert that an Affiliation Invitation sender can be retrieved by the user id."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()

    retrieved_invitation = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(sender_id=invitation.sender_id))
    assert len(retrieved_invitation) > 0
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email
    assert retrieved_invitation[0].token == invitation.token


def test_update_invitation_as_retried(session):
    """Assert that an Affiliation Invitation can be updated."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.FAILED.value)
    invitation.save()
    invitation.update_invitation_as_retried(invitation.sender.id)
    assert invitation
    assert invitation.invitation_status_code == InvitationStatus.PENDING.value


def test_find_invitations_from_org(session):
    """Assert that Affiliation Invitations from a specified org can be retrieved."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()

    found_invitations = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(from_org_id=invitation.from_org_id))
    assert found_invitations
    assert len(found_invitations) == 1
    assert found_invitations[0].from_org_id == invitation.from_org_id
    assert invitation.invitation_status_code == InvitationStatus.PENDING.value


def test_find_invitations_to_org(session):  # pylint:disable=unused-argument
    """Assert that Affiliation Invitations to a specified org can be retrieved."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()

    found_invitations = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(to_org_id=invitation.to_org_id))
    assert found_invitations
    assert len(found_invitations) == 1
    assert found_invitations[0].to_org_id == invitation.to_org_id
    assert invitation.invitation_status_code == InvitationStatus.PENDING.value


def test_find_invitations_by_entity(session):  # pylint:disable=unused-argument
    """Assert that Affiliation Invitation for an entity can be retrieved."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()

    found_invitations = AffiliationInvitationModel.find_invitations_by_entity(invitation.entity_id)
    assert found_invitations
    assert len(found_invitations) == 1
    assert found_invitations[0].entity_id == invitation.entity_id
    assert invitation.invitation_status_code == InvitationStatus.PENDING.value


def test_find_pending_invitations_by_sender(session):  # pylint:disable=unused-argument
    """Assert that pending Affiliation Invitations can be retrieved by the sender user id."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()

    retrieved_invitation = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(sender_id=invitation.sender_id,
                                               status_codes=[InvitationStatus.PENDING.value]))
    assert len(retrieved_invitation) == 1
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email
    assert invitation.invitation_status_code == InvitationStatus.PENDING.value


def test_find_pending_invitations_by_from_org(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation Invitation can be retrieved by the from org id."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()

    retrieved_invitation = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(from_org_id=invitation.from_org_id))
    assert len(retrieved_invitation) == 1
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email
    assert invitation.invitation_status_code == InvitationStatus.PENDING.value


def test_find_pending_invitations_by_to_org(session):  # pylint:disable=unused-argument
    """Assert that an Affiliation Invitation can be retrieved by the to org id."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()

    retrieved_invitation = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(to_org_id=invitation.to_org_id))
    assert len(retrieved_invitation) == 1
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email
    assert invitation.invitation_status_code == InvitationStatus.PENDING.value


def test_invitations_by_status(session):
    """Assert that an Affiliation Invitation can be retrieved by the status."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()

    retrieved_invitation = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(sender_id=invitation.sender_id,
                                               status_codes=[InvitationStatus.PENDING.value]))
    assert len(retrieved_invitation) == 1

    retrieved_invitation = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(sender_id=invitation.sender_id, status_codes=['INVALID']))
    assert len(retrieved_invitation) == 0


def test_invitations_by_expired_status(session):
    """Assert that an Affiliation Invitation can be retrieved when explicitly set EXPIRED."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.EXPIRED.value)
    invitation.save()

    retrieved_invitation = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(sender_id=invitation.sender_id,
                                               status_codes=[InvitationStatus.EXPIRED.value]))
    assert len(retrieved_invitation) == 1

    retrieved_invitation = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(sender_id=invitation.sender_id, status_codes=['INVALID']))
    assert len(retrieved_invitation) == 0


def test_invitations_by_invalid_status(session):
    """Assert that an Affiliation Invitations are not returned with an invalid status."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()

    retrieved_invitation = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(sender_id=invitation.sender_id, status_codes=['INVALID']))
    assert len(retrieved_invitation) == 0


def test_find_invitations_by_org_entity_ids(session):
    """Assert that an Affiliation Invitation can be retrieved by the org and entity ids."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value,
                                                      invitation_type=AffiliationInvitationType.REQUEST.value)
    invitation.save()

    retrieved_invitation = AffiliationInvitationModel.find_invitations_by_org_entity_ids(invitation.from_org_id,
                                                                                         invitation.entity_id)
    assert len(retrieved_invitation) == 1
    assert retrieved_invitation[0].recipient_email == invitation.recipient_email
    assert invitation.invitation_status_code == InvitationStatus.PENDING.value


def test_create_from_dict(session):
    """Assert that an Entity can be created from schema."""
    user = User(username='CP1234567',
                keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')
    user.save()

    org_type = OrgTypeModel(code='TEST', description='Test')
    org_type.save()

    org_status = OrgStatusModel(code='TEST', description='Test')
    org_status.save()

    preferred_payment = PaymentTypeModel(code='TEST', description='Test')
    preferred_payment.save()

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
    user.save()

    result_invitation = AffiliationInvitationModel.create_from_dict(None, user.id)

    assert result_invitation is None


def test_invitations_status_expiry(session):
    """Assert can set the status from PENDING to EXPIRED."""
    sent_date = datetime.now() - timedelta(minutes=int(get_named_config().AFFILIATION_TOKEN_EXPIRY_PERIOD_MINS))
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value,
                                                      sent_date=sent_date)
    invitation.save()

    result: str = invitation.status

    assert result == InvitationStatus.EXPIRED.value


def test_invitations_status_for_request_does_not_expire(session):
    """Assert status stays PENDING for invitation of type REQUEST."""
    sent_date = datetime.now() - timedelta(minutes=int(get_named_config().AFFILIATION_TOKEN_EXPIRY_PERIOD_MINS))
    invitation = factory_affiliation_invitation_model(session=session,
                                                      status=InvitationStatus.PENDING.value,
                                                      sent_date=sent_date,
                                                      invitation_type=AffiliationInvitationType.REQUEST.value)
    session.add(invitation)
    session.commit()

    result: str = invitation.status

    assert result == InvitationStatus.PENDING.value


def test_update_invitation_as_failed(session):
    """Assert that an Affiliation Invitation can be FAILED (e.g. reject authorization request for REQUEST type)."""
    invitation = factory_affiliation_invitation_model(session=session, status=InvitationStatus.PENDING.value)
    invitation.save()
    invitation.set_status(InvitationStatus.FAILED.value)
    assert invitation
    assert invitation.invitation_status_code == InvitationStatus.FAILED.value


def _setup_multiple_orgs_and_invites(session, create_org_count=5, create_affiliation_invitation_count=5):
    user = User(username='CP1234567',
                keycloak_guid='1b20db59-19a0-4727-affe-c6f64309fd04')

    session.add(user)
    session.commit()

    org_type = OrgTypeModel(code='TEST', description='Test')
    org_type.save()

    org_status = OrgStatusModel(code='TEST', description='Test')
    org_status.save()

    preferred_payment = PaymentTypeModel(code='TEST', description='Test')
    preferred_payment.save()

    for i in range(1, create_org_count + 1):
        new_org = _create_org(new_org_id=i, org_type=org_type, org_status=org_status,
                              preferred_payment=preferred_payment)
        session.add(new_org)

    session.commit()

    entity = EntityModel(business_identifier='CP1234567', business_number='791861073BC0001', name='Interesting, Inc.',
                         corp_type_code='CP', id=1)
    entity.save()

    for i in range(1, create_affiliation_invitation_count + 1):
        if i == 1:
            new_ai = _get_random_affiliation_invitation_model(user=user, to_org_id=2, from_org_id=1,
                                                              entity_id=entity.id)
        else:
            new_ai = _get_random_affiliation_invitation_model(user=user, to_org_id=1, from_org_id=i,
                                                              entity_id=entity.id)
        session.add(new_ai)

    session.commit()


def test_find_all_related_to_org(session):
    """Assert that finding affiliations related to org returns correct count."""
    affiliation_invitation_count = 5
    _setup_multiple_orgs_and_invites(session, create_affiliation_invitation_count=affiliation_invitation_count)
    affiliation_invitations: List = AffiliationInvitationModel.find_all_related_to_org(org_id=1)
    assert len(affiliation_invitations) == affiliation_invitation_count


def test_find_all_sent_to_org_affiliated_with_entity(session):
    """Assert that finding affiliations sent to org and requested for specific entity return correct count."""
    affiliation_invitation_count = 5
    _setup_multiple_orgs_and_invites(session, create_affiliation_invitation_count=affiliation_invitation_count)
    affiliation_invitations: List = AffiliationInvitationModel \
        .filter_by(AffiliationInvitationSearch(to_org_id='1', entity_id='1'))
    assert len(affiliation_invitations) == affiliation_invitation_count - 1

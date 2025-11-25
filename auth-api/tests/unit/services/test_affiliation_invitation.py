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
from unittest import mock
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from sbc_common_components.utils.enums import QueueMessageTypes

import auth_api.services.authorization as auth
import auth_api.utils.account_mailer
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import AffiliationInvitation as AffiliationInvitationModel
from auth_api.models import Entity as EntityModel
from auth_api.models import InvitationStatus as InvitationStatusModel
from auth_api.models import Org as OrgModel
from auth_api.models.dataclass import AffiliationInvitationSearch
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import AffiliationInvitation as AffiliationInvitationService
from auth_api.services import Entity as EntityService
from auth_api.services import Org as OrgService
from auth_api.services import User
from auth_api.utils import roles
from auth_api.utils.enums import InvitationStatus
from tests.conftest import mock_token
from tests.utilities.factory_scenarios import TestContactInfo, TestEntityInfo, TestJwtClaims, TestOrgInfo, TestUserInfo
from tests.utilities.factory_utils import (
    factory_affiliation_invitation,
    factory_entity_model,
    factory_membership_model,
    factory_user_model,
    patch_token_info,
)


def create_test_entity():
    """Create test entity data."""
    entity = EntityService.save_entity(
        {
            "businessIdentifier": TestEntityInfo.entity_passcode["businessIdentifier"],
            "businessNumber": TestEntityInfo.entity_passcode["businessNumber"],
            "passCode": TestEntityInfo.entity_passcode["passCode"],
            "name": TestEntityInfo.entity_passcode["name"],
            "corpTypeCode": TestEntityInfo.entity_passcode["corpTypeCode"],
        }
    )

    entity.add_contact(TestContactInfo.contact1)
    return entity


def setup_org_and_entity(user):
    """Create test org and entity data."""
    from_org = OrgService.create_org(TestOrgInfo.affiliation_from_org, user_id=user.id)
    to_org = OrgService.create_org(TestOrgInfo.affiliation_to_org, user_id=user.id)
    entity = create_test_entity()
    from_org_dictionary = from_org.as_dict()
    to_org_dictionary = to_org.as_dict()
    entity_dictionary = entity.as_dict()

    return from_org_dictionary, to_org_dictionary, entity_dictionary


@pytest.mark.parametrize(
    "business_data,default_name,business_identifier,expected_name",
    [
        # Test case 1: Full LEAR response structure with matching alternate name
        (
            {
                "business": {
                    "identifier": "FM0000123",
                    "legalName": "John Smith",
                    "legalType": "SP",
                    "alternateNames": [{"identifier": "FM0000123", "name": "Smith's Construction"}],
                }
            },
            "John Smith",
            "FM0000123",
            "Smith's Construction",
        ),
        # Test case 2: Direct business object structure with matching alternate name
        (
            {
                "identifier": "FM0000123",
                "legalName": "John Smith",
                "legalType": "SP",
                "alternateNames": [{"identifier": "FM0000123", "name": "Smith's Construction"}],
            },
            "John Smith",
            "FM0000123",
            "Smith's Construction",
        ),
        # Test case 3: No matching alternate name (different identifier)
        (
            {
                "business": {
                    "identifier": "FM0000123",
                    "legalName": "John Smith",
                    "legalType": "SP",
                    "alternateNames": [{"identifier": "FM0000999", "name": "Other Business"}],
                }
            },
            "John Smith",
            "FM0000123",
            "John Smith",  # Should return default name
        ),
        # Test case 4: No alternate names at all
        (
            {
                "business": {
                    "identifier": "FM0000123",
                    "legalName": "John Smith",
                    "legalType": "SP",
                    "alternateNames": [],
                }
            },
            "John Smith",
            "FM0000123",
            "John Smith",  # Should return default name
        ),
        # Test case 5: alternateNames field missing
        (
            {"business": {"identifier": "FM0000123", "legalName": "John Smith", "legalType": "SP"}},
            "John Smith",
            "FM0000123",
            "John Smith",  # Should return default name
        ),
        # Test case 6: Multiple alternate names, only first matching one is used
        (
            {
                "business": {
                    "identifier": "FM0000123",
                    "legalName": "John Smith",
                    "legalType": "SP",
                    "alternateNames": [
                        {"identifier": "FM0000123", "name": "Smith's Construction"},
                        {"identifier": "FM0000123", "name": "John's Business"},
                    ],
                }
            },
            "John Smith",
            "FM0000123",
            "Smith's Construction",  # Should return first matching alternate name
        ),
    ],
)
def test_get_business_name_from_alternative_name(business_data, default_name, business_identifier, expected_name):
    """Test get_business_name_from_alternative_name method with various scenarios."""
    result = AffiliationInvitationService.get_business_name_from_alternative_name(
        business_data, default_name, business_identifier
    )
    assert result == expected_name


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
@pytest.mark.parametrize(
    "business_entities,expected_names",
    [
        # Test case 1: SP firm with alternate name
        (
            [
                {
                    "identifier": "FM0000123",
                    "legalName": "John Smith",
                    "legalType": "SP",
                    "state": "ACTIVE",
                    "alternateNames": [{"identifier": "FM0000123", "name": "Smith's Construction"}],
                }
            ],
            ["Smith's Construction"],  # Should use alternate name
        ),
        # Test case 2: GP firm with alternate name
        (
            [
                {
                    "identifier": "FM0000124",
                    "legalName": "Smith & Jones",
                    "legalType": "GP",
                    "state": "ACTIVE",
                    "alternateNames": [{"identifier": "FM0000124", "name": "Smith Jones Construction Partnership"}],
                }
            ],
            ["Smith Jones Construction Partnership"],  # Should use alternate name
        ),
        # Test case 3: SP firm without alternate name
        (
            [{"identifier": "FM0000125", "legalName": "Jane Doe", "legalType": "SP", "state": "ACTIVE"}],
            ["Jane Doe"],  # Should use legal name
        ),
        # Test case 4: Non-SP/GP firm (should always use legal name)
        (
            [
                {
                    "identifier": "BC0000126",
                    "legalName": "ABC Corp",
                    "legalType": "BC",
                    "state": "ACTIVE",
                    "alternateNames": [{"identifier": "BC0000126", "name": "ABC Corporation"}],
                }
            ],
            ["ABC Corp"],  # Should use legal name even with alternate name
        ),
        # Test case 5: Mixed firms
        (
            [
                {
                    "identifier": "FM0000127",
                    "legalName": "Alice Smith",
                    "legalType": "SP",
                    "state": "ACTIVE",
                    "alternateNames": [{"identifier": "FM0000127", "name": "Alice's Bakery"}],
                },
                {
                    "identifier": "BC0000128",
                    "legalName": "XYZ Inc",
                    "legalType": "BC",
                    "state": "ACTIVE",
                    "alternateNames": [{"identifier": "BC0000128", "name": "XYZ Corporation"}],
                },
            ],
            ["Alice's Bakery", "XYZ Inc"],  # SP uses alternate, BC uses legal
        ),
    ],
)
def test_enrich_affiliation_invitations_with_business_name_logic(monkeypatch, business_entities, expected_names):
    """Test that enrich_affiliation_invitations_dict_list_with_business_data uses correct names for SP/GP firms."""

    # Mock the _get_multiple_business_details method to return our test data
    def mock_get_multiple_business_details(business_identifiers, token):
        return business_entities

    monkeypatch.setattr(
        "auth_api.services.affiliation_invitation.AffiliationInvitation._get_multiple_business_details",
        mock_get_multiple_business_details,
    )

    # Create test affiliation invitation dictionaries
    affiliation_invitation_dicts = []
    for i, business_entity in enumerate(business_entities):
        affiliation_invitation_dicts.append(
            {
                "id": i + 1,
                "business_identifier": business_entity["identifier"],
                "from_org": {"id": 100, "name": "Test Org", "org_type": "PREMIUM"},
                "to_org": None,
                "status": "PENDING",
                "type": "EMAIL",
            }
        )

    # Call the method under test
    result = AffiliationInvitationService.enrich_affiliation_invitations_dict_list_with_business_data(
        affiliation_invitation_dicts
    )

    # Verify the results
    assert len(result) == len(expected_names)
    for i, expected_name in enumerate(expected_names):
        assert result[i].entity.name == expected_name
        assert result[i].entity.business_identifier == business_entities[i]["identifier"]
        assert result[i].entity.corp_type == business_entities[i]["legalType"]
        assert result[i].entity.state == business_entities[i]["state"]


def test_enrich_affiliation_invitations_empty_list():
    """Test that empty list is handled correctly."""
    result = AffiliationInvitationService.enrich_affiliation_invitations_dict_list_with_business_data([])
    assert result == []


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_enrich_affiliation_invitations_missing_business_entity(monkeypatch):
    """Test handling when business entity is not found in the response."""

    # Mock to return empty list (no matching business entities)
    def mock_get_multiple_business_details(business_identifiers, token):
        return []

    monkeypatch.setattr(
        "auth_api.services.affiliation_invitation.AffiliationInvitation._get_multiple_business_details",
        mock_get_multiple_business_details,
    )

    affiliation_invitation_dicts = [
        {
            "id": 1,
            "business_identifier": "FM0000999",
            "from_org": {"id": 100, "name": "Test Org", "org_type": "PREMIUM"},
            "to_org": None,
            "status": "PENDING",
            "type": "EMAIL",
        }
    ]

    result = AffiliationInvitationService.enrich_affiliation_invitations_dict_list_with_business_data(
        affiliation_invitation_dicts
    )

    # Should still create the object but with None entity
    assert len(result) == 1
    assert result[0].entity is None


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_as_dict(session, auth_mock, keycloak_mock, business_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that the Affiliation Invitation is exported correctly as a dictionary."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        user = factory_user_model()
        patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)

        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary["id"],
            to_org_id=to_org_dictionary["id"],
            business_identifier=entity_dictionary["business_identifier"],
        )

        affiliation_invitation = AffiliationInvitationService.create_affiliation_invitation(
            affiliation_invitation_info, User(user)
        )
        affiliation_invitation_dictionary = affiliation_invitation.as_dict()
        assert affiliation_invitation_dictionary["recipient_email"] == affiliation_invitation_info["recipientEmail"]


@pytest.mark.parametrize(
    "create_org_with",
    [
        ("id"),
        ("uuid"),
    ],
)
@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_create_affiliation_invitation(session, auth_mock, keycloak_mock, business_mock, monkeypatch, create_org_with):  # pylint:disable=unused-argument
    """Assert that an Affiliation Invitation can be created."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)

        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary["id"],
            to_org_id=to_org_dictionary["id"] if create_org_with == "id" else None,
            to_org_uuid=to_org_dictionary["uuid"] if create_org_with == "uuid" else None,
            business_identifier=entity_dictionary["business_identifier"],
        )

        affiliation_invitation = AffiliationInvitationService.create_affiliation_invitation(
            affiliation_invitation_info, User(user)
        )
        invitation_dictionary = affiliation_invitation.as_dict()
        assert invitation_dictionary["recipient_email"] == affiliation_invitation_info["recipientEmail"]
        assert invitation_dictionary["id"]


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_find_affiliation_invitation_by_id(session, auth_mock, keycloak_mock, business_mock, monkeypatch):  # pylint:disable=unused-argument
    """Find an existing affiliation invitation with the provided id."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)

        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary["id"],
            to_org_id=to_org_dictionary["id"],
            business_identifier=entity_dictionary["business_identifier"],
        )

        new_invitation = AffiliationInvitationService.create_affiliation_invitation(
            affiliation_invitation_info, User(user)
        ).as_dict()
        invitation = AffiliationInvitationService.find_affiliation_invitation_by_id(new_invitation["id"]).as_dict()

        assert invitation
        assert invitation["recipient_email"] == affiliation_invitation_info["recipientEmail"]


def test_find_invitation_by_id_exception(session, auth_mock):  # pylint:disable=unused-argument
    """Find an existing affiliation invitation with the provided id with exception."""
    affiliation_invitation = AffiliationInvitationService.find_affiliation_invitation_by_id(None)
    assert affiliation_invitation is None


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_delete_affiliation_invitation(session, auth_mock, keycloak_mock, business_mock, monkeypatch):  # pylint:disable=unused-argument
    """Delete the specified affiliation invitation."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary["id"],
            to_org_id=to_org_dictionary["id"],
            business_identifier=entity_dictionary["business_identifier"],
        )

        new_invitation = AffiliationInvitationService.create_affiliation_invitation(
            affiliation_invitation_info, User(user)
        ).as_dict()
        AffiliationInvitationService.delete_affiliation_invitation(new_invitation["id"])
        invitation = AffiliationInvitationService.find_affiliation_invitation_by_id(new_invitation["id"])
        assert invitation is None


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_delete_accepted_affiliation_invitation(
    session, auth_mock, keycloak_mock, business_mock, entity_mapping_mock, monkeypatch
):  # pylint:disable=unused-argument
    """Delete the specified accepted affiliation invitation."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary["id"],
            to_org_id=to_org_dictionary["id"],
            business_identifier=entity_dictionary["business_identifier"],
        )

        new_invitation = AffiliationInvitationService.create_affiliation_invitation(
            affiliation_invitation_info, User(user)
        ).as_dict()

        invitation = AffiliationInvitationService.accept_affiliation_invitation(
            new_invitation["id"], User(user), ""
        ).as_dict()
        assert invitation
        assert invitation["status"] == InvitationStatus.ACCEPTED.value

        AffiliationInvitationService.delete_affiliation_invitation(new_invitation["id"])
        deleted_invitation = AffiliationInvitationService.find_affiliation_invitation_by_id(new_invitation["id"])
        assert deleted_invitation
        assert deleted_invitation.as_dict().get("is_deleted")


def test_delete_affiliation_invitation_exception(session, auth_mock):  # pylint:disable=unused-argument
    """Delete the specified affiliation invitation with exception."""
    with pytest.raises(BusinessException) as exception:
        AffiliationInvitationService.delete_affiliation_invitation(None)

    assert exception.value.code == Error.DATA_NOT_FOUND.name


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_update_affiliation_invitation(session, auth_mock, keycloak_mock, business_mock, monkeypatch):  # pylint:disable=unused-argument
    """Update the specified affiliation invitation with new data."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary["id"],
            to_org_id=to_org_dictionary["id"],
            business_identifier=entity_dictionary["business_identifier"],
        )

        new_invitation = AffiliationInvitationService.create_affiliation_invitation(
            affiliation_invitation_info, User(user)
        )
        updated_invitation = new_invitation.update_affiliation_invitation(User(user), {}).as_dict()
        assert updated_invitation["status"] == "PENDING"


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_update_invitation_verify_different_tokens(session, auth_mock, keycloak_mock, business_mock, monkeypatch):  # pylint:disable=unused-argument
    """Update the specified affiliation invitation to check for token difference."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary["id"],
            to_org_id=to_org_dictionary["id"],
            business_identifier=entity_dictionary["business_identifier"],
        )

        new_invitation = AffiliationInvitationService.create_affiliation_invitation(
            affiliation_invitation_info, User(user)
        )
        new_invitation_id = new_invitation.as_dict().get("id")
        invitation_model = AffiliationInvitationModel.find_by_id(new_invitation_id)
        old_token = invitation_model.token
        with freeze_time(
            lambda: datetime.now() + timedelta(seconds=1)
        ):  # to give time difference..or else token will be same..
            updated_invitation = new_invitation.update_affiliation_invitation(User(user), {}).as_dict()
            updated_invitation_model = AffiliationInvitationModel.find_by_id(new_invitation_id)
            new_token = updated_invitation_model.token
        assert old_token != new_token
        assert updated_invitation["status"] == "PENDING"


def test_generate_confirmation_token(session):  # pylint:disable=unused-argument
    """Generate the affiliation invitation token."""
    confirmation_token = AffiliationInvitationService.generate_confirmation_token(1, 2, 3, "CP1234567")
    assert confirmation_token is not None


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_validate_token_accepted(session, auth_mock, keycloak_mock, business_mock, entity_mapping_mock, monkeypatch):  # pylint:disable=unused-argument
    """Validate invalid invitation token."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        user = factory_user_model(TestUserInfo.user_test)
        user_invitee = factory_user_model(TestUserInfo.user1)
        patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_dictionary["id"],
            to_org_id=to_org_dictionary["id"],
            business_identifier=entity_dictionary["business_identifier"],
        )

        new_invitation = AffiliationInvitationService.create_affiliation_invitation(
            affiliation_invitation_info, User(user_invitee)
        ).as_dict()
        token = AffiliationInvitationService.generate_confirmation_token(
            new_invitation["id"],
            new_invitation["from_org"]["id"],
            new_invitation["to_org"]["id"],
            entity_dictionary["business_identifier"],
        )

        AffiliationInvitationService.accept_affiliation_invitation(new_invitation["id"], User(user_invitee), "")

        with pytest.raises(BusinessException) as exception:
            AffiliationInvitationService.validate_token(token, new_invitation["id"])

        assert exception.value.code == Error.ACTIONED_AFFILIATION_INVITATION.name


def test_validate_token_exception(session):  # pylint:disable=unused-argument
    """Validate the affiliation invitation token with exception."""
    with pytest.raises(BusinessException) as exception:
        AffiliationInvitationService.validate_token(None, 1)

    assert exception.value.code == Error.EXPIRED_AFFILIATION_INVITATION.name


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_accept_affiliation_invitation(
    publish_mock, session, auth_mock, keycloak_mock, business_mock, entity_mapping_mock, monkeypatch
):  # pylint:disable=unused-argument
    """Accept the affiliation invitation and add the affiliation from the invitation."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        with patch.object(auth, "check_auth", return_value=True):
            user_with_token = dict(TestUserInfo.user_test)
            user_with_token["keycloak_guid"] = TestJwtClaims.public_user_role["sub"]
            user_with_token["idp_userid"] = TestJwtClaims.public_user_role["idp_userid"]
            user = factory_user_model(user_with_token)
            patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)

            from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

            affiliation_invitation_info = factory_affiliation_invitation(
                from_org_id=from_org_dictionary["id"],
                to_org_id=to_org_dictionary["id"],
                business_identifier=entity_dictionary["business_identifier"],
            )

            user_with_token_invitee = dict(TestUserInfo.user1)
            user_with_token_invitee["keycloak_guid"] = TestJwtClaims.edit_role_2["sub"]
            user_invitee = factory_user_model(user_with_token_invitee)

            new_invitation = AffiliationInvitationService.create_affiliation_invitation(
                affiliation_invitation_info, User(user_invitee)
            ).as_dict()

            invitation = AffiliationInvitationService.accept_affiliation_invitation(
                new_invitation["id"], User(user_invitee), ""
            ).as_dict()
            patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
            affiliation = AffiliationService.find_affiliation(
                new_invitation["from_org"]["id"], entity_dictionary["business_identifier"]
            )
            assert affiliation
            assert invitation
            assert affiliation["id"] == invitation["affiliation_id"]


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_accept_invitation_exceptions(
    session, auth_mock, keycloak_mock, business_mock, entity_mapping_mock, monkeypatch
):  # pylint:disable=unused-argument
    """Accept the affiliation invitation exceptions."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        with patch.object(auth, "check_auth", return_value=True):
            user = factory_user_model(TestUserInfo.user_test)
            patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)
            from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

            affiliation_invitation_info = factory_affiliation_invitation(
                from_org_id=from_org_dictionary["id"],
                to_org_id=to_org_dictionary["id"],
                business_identifier=entity_dictionary["business_identifier"],
            )

            user_invitee = factory_user_model(TestUserInfo.user1)

            # Accepting a non-existent invitation should raise not found exception
            with pytest.raises(BusinessException) as exception:
                AffiliationInvitationService.accept_affiliation_invitation(None, User(user_invitee), "")

            assert exception.value.code == Error.DATA_NOT_FOUND.name

            # Accepting an invitation multiple times should raise actioned invitation exception
            new_invitation = AffiliationInvitationService.create_affiliation_invitation(
                affiliation_invitation_info, User(user_invitee)
            ).as_dict()

            AffiliationInvitationService.accept_affiliation_invitation(new_invitation["id"], User(user_invitee), "")

            with pytest.raises(BusinessException) as exception:
                AffiliationInvitationService.accept_affiliation_invitation(new_invitation["id"], User(user_invitee), "")

            assert exception.value.code == Error.ACTIONED_AFFILIATION_INVITATION.name

            # Accepting an expired invitation should raise an expired invitation exception
            with pytest.raises(BusinessException) as exception:
                expired_invitation: AffiliationInvitationModel = AffiliationInvitationModel.find_invitation_by_id(
                    new_invitation["id"]
                )
                expired_invitation.invitation_status = InvitationStatusModel.get_status_by_code("EXPIRED")
                expired_invitation.save()
                AffiliationInvitationService.accept_affiliation_invitation(
                    expired_invitation.id, User(user_invitee), ""
                )
            assert exception.value.code == Error.EXPIRED_AFFILIATION_INVITATION.name


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_get_invitations_by_from_org_id(session, auth_mock, keycloak_mock, business_mock, monkeypatch):  # pylint:disable=unused-argument
    """Find an existing invitation with the provided from org id."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
        user_with_token = dict(TestUserInfo.user_test)
        user_with_token["keycloak_guid"] = TestJwtClaims.public_user_role["sub"]
        user = factory_user_model(user_with_token)
        patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        from_org_id = from_org_dictionary["id"]
        to_org_id = to_org_dictionary["id"]
        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_id, to_org_id=to_org_id, business_identifier=entity_dictionary["business_identifier"]
        )

        AffiliationInvitationService.create_affiliation_invitation(affiliation_invitation_info, User(user))

        invitations: list = AffiliationInvitationService.search_invitations(
            AffiliationInvitationSearch(from_org_id=from_org_id, status_codes=["PENDING"])
        )
        assert invitations
        assert len(invitations) == 1


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_get_invitations_by_to_org_id(session, auth_mock, keycloak_mock, business_mock, monkeypatch):  # pylint:disable=unused-argument
    """Find an existing invitation with the provided to org id."""
    with patch.object(AffiliationInvitationService, "send_affiliation_invitation", return_value=None):
        patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
        user_with_token = dict(TestUserInfo.user_test)
        user_with_token["keycloak_guid"] = TestJwtClaims.public_user_role["sub"]
        user = factory_user_model(user_with_token)
        patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)
        from_org_dictionary, to_org_dictionary, entity_dictionary = setup_org_and_entity(user)

        from_org_id = from_org_dictionary["id"]
        to_org_id = to_org_dictionary["id"]
        affiliation_invitation_info = factory_affiliation_invitation(
            from_org_id=from_org_id, to_org_id=to_org_id, business_identifier=entity_dictionary["business_identifier"]
        )

        AffiliationInvitationService.create_affiliation_invitation(affiliation_invitation_info, User(user))

        invitations: list = AffiliationInvitationService.search_invitations(
            search_filter=AffiliationInvitationSearch(to_org_id=to_org_id, status_codes=["PENDING"])
        )
        assert invitations
        assert len(invitations) == 1


def _setup_affiliation_invitation_data(
    affiliation_invitation_type="EMAIL", affiliation_invitation_status_code=InvitationStatus.PENDING.value
):
    from_org = OrgModel()
    from_org.id = 1
    from_org.name = "From the moon inc."
    from_org.branch_name = "Luna division"
    to_org = OrgModel()
    to_org.id = 2
    to_org.name = "To the stars inc."
    entity = EntityModel()
    entity.business_identifier = "BC1111111"

    affiliation_invitation = AffiliationInvitationModel()
    affiliation_invitation.from_org = from_org
    affiliation_invitation.to_org = to_org
    affiliation_invitation.recipient_email = "abc@test.com"
    affiliation_invitation.from_org_id = from_org.id
    affiliation_invitation.to_org_id = to_org.id
    affiliation_invitation.invitation_status_code = affiliation_invitation_status_code
    affiliation_invitation.type = affiliation_invitation_type
    affiliation_invitation.entity = entity

    return affiliation_invitation


@patch.object(auth_api.services.affiliation_invitation, "publish_to_mailer")
def test_send_affiliation_invitation_magic_link(
    publish_to_mailer_mock, session, auth_mock, keycloak_mock, business_mock, monkeypatch
):
    """Verify Magic link data for email is correctly generated."""
    affiliation_invitation = _setup_affiliation_invitation_data()
    business_name = "Busy Inc."
    affiliation_invitation.token = "ABCD"  # noqa: S105

    AffiliationInvitationService.send_affiliation_invitation(
        affiliation_invitation=affiliation_invitation,
        business_name=business_name,
        email_addresses=affiliation_invitation.recipient_email,
    )

    expected_data = {
        "accountId": affiliation_invitation.from_org.id,
        "businessName": business_name,
        "emailAddresses": affiliation_invitation.recipient_email,
        "orgName": affiliation_invitation.from_org.name,
        "businessIdentifier": affiliation_invitation.entity.business_identifier,
        "contextUrl": "https://localhost.com//affiliationInvitation/acceptToken"
        "?token=ABCD&orgName=RnJvbSB0aGUgbW9vbiBpbmMu",
        "expiryText": "12 hours",
    }

    publish_to_mailer_mock.assert_called_with(
        notification_type=QueueMessageTypes.AFFILIATION_INVITATION.value, data=expected_data
    )


@patch.object(auth_api.services.affiliation_invitation, "publish_to_mailer")
def test_send_affiliation_invitation_request_sent(
    publish_to_mailer_mock, session, auth_mock, keycloak_mock, business_mock, monkeypatch
):
    """Verify REQUEST ACCESS - on create request - data for email is correctly generated."""
    additional_message = "Ad Astra."
    affiliation_invitation = _setup_affiliation_invitation_data(affiliation_invitation_type="REQUEST")
    business_name = "Troll incorporated"
    affiliation_invitation.additional_message = additional_message

    AffiliationInvitationService.send_affiliation_invitation(
        affiliation_invitation=affiliation_invitation,
        business_name=business_name,
        email_addresses=affiliation_invitation.recipient_email,
    )

    expected_data = {
        "accountId": affiliation_invitation.from_org.id,
        "businessName": business_name,
        "emailAddresses": affiliation_invitation.recipient_email,
        "orgName": affiliation_invitation.from_org.name,
        "businessIdentifier": affiliation_invitation.entity.business_identifier,
        "fromOrgName": affiliation_invitation.from_org.name,
        "fromOrgBranchName": affiliation_invitation.from_org.branch_name,
        "toOrgName": affiliation_invitation.to_org.name,
        "toOrgBranchName": affiliation_invitation.to_org.branch_name,
        "additionalMessage": additional_message,
        "expiryText": "12 hours",
    }
    notification_type = QueueMessageTypes.AFFILIATION_INVITATION_REQUEST.value
    publish_to_mailer_mock.assert_called_with(notification_type=notification_type, data=expected_data)


@patch.object(auth_api.services.affiliation_invitation, "publish_to_mailer")
def test_send_affiliation_invitation_request_authorized(
    publish_to_mailer_mock, session, auth_mock, keycloak_mock, business_mock, monkeypatch
):
    """Verify REQUEST ACCESS - on authorize request - data for email is correctly generated."""
    monkeypatch.setattr(
        "auth_api.services.affiliation_invitation.RestService.get_service_account_token",
        lambda config_id, config_secret: "TestToken",  # noqa: ARG005
    )

    affiliation_invitation = _setup_affiliation_invitation_data(
        affiliation_invitation_type="REQUEST", affiliation_invitation_status_code=InvitationStatus.ACCEPTED.value
    )
    business_name = "BarFoo, Inc."  # will get it from business mock 'get_business' method
    expected_email = "expected@email.com"
    business_identifier = "BC1111111"
    monkeypatch.setattr(
        "auth_api.services.affiliation_invitation.UserService.get_admin_emails_for_org",
        lambda org_id: expected_email if org_id == affiliation_invitation.from_org_id else None,
    )

    # simulate subquery for entity
    entity = EntityModel()
    entity.name = business_name
    entity.business_identifier = business_identifier
    affiliation_invitation.entity = entity

    AffiliationInvitationService.send_affiliation_invitation_authorization_email(
        affiliation_invitation=affiliation_invitation, is_authorized=True
    )

    expected_data = {
        "accountId": affiliation_invitation.from_org.id,
        "businessName": business_name,
        "emailAddresses": expected_email,
        "orgName": affiliation_invitation.from_org.name,
        "businessIdentifier": affiliation_invitation.entity.business_identifier,
        "fromOrgName": affiliation_invitation.from_org.name,
        "fromOrgBranchName": affiliation_invitation.from_org.branch_name,
        "toOrgName": affiliation_invitation.to_org.name,
        "toOrgBranchName": affiliation_invitation.to_org.branch_name,
        "isAuthorized": True,
        "expiryText": "12 hours",
    }

    notification_type = QueueMessageTypes.AFFILIATION_INVITATION_REQUEST_AUTHORIZATION.value
    publish_to_mailer_mock.assert_called_with(notification_type=notification_type, data=expected_data)


@patch.object(auth_api.services.affiliation_invitation, "publish_to_mailer")
def test_send_affiliation_invitation_request_refused(
    publish_to_mailer_mock, session, auth_mock, keycloak_mock, business_mock, monkeypatch
):
    """Verify REQUEST ACCESS - on refuse request - data for email is correctly generated."""
    monkeypatch.setattr(
        "auth_api.services.affiliation_invitation.RestService.get_service_account_token",
        lambda config_id, config_secret: "TestToken",  # noqa: ARG005
    )

    affiliation_invitation = _setup_affiliation_invitation_data(
        affiliation_invitation_type="REQUEST", affiliation_invitation_status_code=InvitationStatus.FAILED.value
    )

    expected_email = "expected@email.com"
    monkeypatch.setattr(
        "auth_api.services.affiliation_invitation.UserService.get_admin_emails_for_org",
        lambda org_id: expected_email if org_id == affiliation_invitation.from_org_id else None,
    )

    business_name = "BarFoo, Inc."  # will get it from business mock 'get_business' method
    business_identifier = "BC1111111"

    # simulate subquery for entity
    entity = EntityModel()
    entity.name = business_name
    entity.business_identifier = business_identifier
    affiliation_invitation.entity = entity

    AffiliationInvitationService.send_affiliation_invitation_authorization_email(
        affiliation_invitation=affiliation_invitation, is_authorized=False
    )

    expected_data = {
        "accountId": affiliation_invitation.from_org.id,
        "businessName": business_name,
        "emailAddresses": expected_email,
        "orgName": affiliation_invitation.from_org.name,
        "businessIdentifier": affiliation_invitation.entity.business_identifier,
        "fromOrgName": affiliation_invitation.from_org.name,
        "fromOrgBranchName": affiliation_invitation.from_org.branch_name,
        "toOrgName": affiliation_invitation.to_org.name,
        "toOrgBranchName": affiliation_invitation.to_org.branch_name,
        "isAuthorized": False,
        "expiryText": "12 hours",
    }

    notification_type = QueueMessageTypes.AFFILIATION_INVITATION_REQUEST_AUTHORIZATION.value
    publish_to_mailer_mock.assert_called_with(notification_type=notification_type, data=expected_data)


@pytest.mark.parametrize(
    "test_name,member_type,expect_request_invites",
    [
        ("test user is org admin", roles.ADMIN, True),
        ("test user is org coordinator", roles.COORDINATOR, True),
        ("test user is org user", roles.USER, True),
    ],
)
@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_get_all_invitations_with_details_related_to_org(
    session, auth_mock, keycloak_mock, business_mock, monkeypatch, test_name, member_type, expect_request_invites
):
    """Verify REQUEST affiliation invitations are returned only when user is org ADMIN/COORDINATOR."""
    # setup an org
    user = factory_user_model(TestUserInfo.user_test)
    patch_token_info({"sub": user.keycloak_guid, "idp_userid": user.idp_userid}, monkeypatch)
    org1 = OrgService.create_org(TestOrgInfo.org1, user_id=user.id)
    assert org1
    org2 = OrgService.create_org(TestOrgInfo.org3, user_id=user.id)
    assert org2
    org3 = OrgService.create_org(TestOrgInfo.org4, user_id=user.id)
    assert org3
    entity = factory_entity_model()

    affiliation_invitation_model1 = AffiliationInvitationModel.create_from_dict(
        invitation_info={
            "fromOrgId": org1._model.id,
            "toOrgId": org2._model.id,
            "entityId": entity.id,
            "type": "REQUEST",
        },
        user_id=user.id,
    )
    affiliation_invitation_model1.save()

    affiliation_invitation_model2 = AffiliationInvitationModel.create_from_dict(
        invitation_info={
            "fromOrgId": org1._model.id,
            "toOrgId": org3._model.id,
            "entityId": entity.id,
            "type": "REQUEST",
        },
        user_id=user.id,
    )
    affiliation_invitation_model2.save()

    factory_membership_model(user.id, org1._model.id, member_type=member_type)

    search_filter = AffiliationInvitationSearch()
    result = AffiliationInvitationService.get_all_invitations_with_details_related_to_org(
        org_id=org1._model.id, search_filter=search_filter
    )

    if expect_request_invites:
        assert len(result) == 2
    else:
        assert result == []

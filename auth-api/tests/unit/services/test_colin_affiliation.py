# Copyright © 2026 Province of British Columbia
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
"""Tests for affiliating COLIN businesses that are not loaded in LEAR.

Covers the on demand entity creation/re-sync from COLIN, the passcode guard, and the
affiliation details fallback used to render these businesses on the dashboard.
"""

import pytest

from auth_api.models.dataclass import AffiliationSearchDetails
from auth_api.models.entity import Entity as EntityModel
from auth_api.services.affiliation import Affiliation as AffiliationService
from auth_api.services.colin import Colin as ColinService
from auth_api.services.entity import Entity as EntityService
from auth_api.utils.passcode import passcode_hash
from tests.utilities.factory_scenarios import TestJwtClaims
from tests.utilities.factory_utils import patch_token_info

COLIN_IDENTIFIER = "BC0870226"

COLIN_ENTITY_INFO = {
    "identifier": "0870226",
    "legalName": "COLIN TEST COMPANY LTD.",
    "legalType": "BC",
    "status": "Active",
    "goodStanding": True,
    "businessNumber": "791861078BC0001",
    "adminFreeze": False,
    "email": "registered.office@test.com",
    "passCode": "111111111",
}


def _colin_info(**overrides):
    """Return a COLIN auth-info payload with overrides applied."""
    return {**COLIN_ENTITY_INFO, **overrides}


@pytest.mark.parametrize(
    "identifier, expected",
    [
        ("BC0870226", True),
        ("BC1234567", True),
        ("CP1234567", False),  # coop
        ("FM1234567", False),  # firm
        ("NR 1234567", False),  # name request
        ("T7654321", False),  # temp registration
        ("BC123456", False),  # too few digits
        ("BC12345678", False),  # too many digits
        ("", False),
        (None, False),
    ],
)
def test_is_colin_identifier(identifier, expected):
    """Assert only BC style corp numbers are treated as COLIN candidates."""
    assert ColinService.is_colin_identifier(identifier) is expected


@pytest.mark.parametrize(
    "corp_type, expected",
    [
        ("BC", True),
        ("ULC", True),
        ("CC", True),
        ("bc", True),
        ("BEN", False),
        ("CP", False),
        ("SP", False),
        (None, False),
    ],
)
def test_is_affiliation_eligible_type(app, corp_type, expected):  # pylint:disable=unused-argument
    """Assert only the in scope corp types may be affiliated from COLIN."""
    assert ColinService.is_affiliation_eligible_type(corp_type) is expected


def test_sync_from_colin_creates_entity(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert an entity is created on demand from COLIN data."""
    monkeypatch.setattr(ColinService, "fetch_auth_info", staticmethod(lambda _: _colin_info()))

    entity = EntityService.sync_from_colin(COLIN_IDENTIFIER)

    assert entity is not None
    assert entity.business_identifier == COLIN_IDENTIFIER
    assert entity.name == "COLIN TEST COMPANY LTD."
    assert entity.corp_type == "BC"
    # COLIN reports 'Active'; auth stores LEAR style states
    assert entity.status == "ACTIVE"
    assert entity.is_loaded_lear is False
    # the passcode is stored hashed, never in the clear
    assert entity.pass_code is not None
    assert entity.pass_code != COLIN_ENTITY_INFO["passCode"]
    # the registered office email is stored as the entity contact for the email invitation flow
    assert entity.get_contact().email == "registered.office@test.com"


def test_sync_from_colin_refreshes_existing_entity(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert a re-sync updates the stored passcode, email and name from COLIN."""
    monkeypatch.setattr(ColinService, "fetch_auth_info", staticmethod(lambda _: _colin_info()))
    EntityService.sync_from_colin(COLIN_IDENTIFIER)

    original = EntityModel.find_by_business_identifier(COLIN_IDENTIFIER)
    original_hash = original.pass_code

    monkeypatch.setattr(
        ColinService,
        "fetch_auth_info",
        staticmethod(
            lambda _: _colin_info(
                legalName="RENAMED COMPANY LTD.",
                passCode="999999999",
                email="new.office@test.com",
                status="Historical",
            )
        ),
    )
    entity = EntityService.sync_from_colin(COLIN_IDENTIFIER)

    assert entity.name == "RENAMED COMPANY LTD."
    assert entity.status == "HISTORICAL"
    assert entity.pass_code != original_hash
    assert entity.get_contact().email == "new.office@test.com"
    assert entity.is_loaded_lear is False


def test_sync_from_colin_ignores_out_of_scope_corp_type(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert corp types outside BC/ULC/CC are not created from COLIN."""
    monkeypatch.setattr(ColinService, "fetch_auth_info", staticmethod(lambda _: _colin_info(legalType="BEN")))

    assert EntityService.sync_from_colin(COLIN_IDENTIFIER) is None
    assert EntityModel.find_by_business_identifier(COLIN_IDENTIFIER) is None


def test_sync_from_colin_handles_missing_business(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert nothing is created when COLIN has no record of the business."""
    monkeypatch.setattr(ColinService, "fetch_auth_info", staticmethod(lambda _: None))

    assert EntityService.sync_from_colin(COLIN_IDENTIFIER) is None
    assert EntityModel.find_by_business_identifier(COLIN_IDENTIFIER) is None


def test_sync_from_colin_keeps_passcode_when_colin_has_none(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert an empty COLIN passcode does not silently clear the stored credential."""
    monkeypatch.setattr(ColinService, "fetch_auth_info", staticmethod(lambda _: _colin_info()))
    EntityService.sync_from_colin(COLIN_IDENTIFIER)
    original_hash = EntityModel.find_by_business_identifier(COLIN_IDENTIFIER).pass_code

    monkeypatch.setattr(ColinService, "fetch_auth_info", staticmethod(lambda _: _colin_info(passCode=None)))
    entity = EntityService.sync_from_colin(COLIN_IDENTIFIER)

    assert entity.pass_code == original_hash


def test_colin_entity_without_passcode_is_not_openly_affiliatable(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert a COLIN entity with no passcode denies affiliation instead of falling through.

    An entity with a null passcode is otherwise affiliatable by anyone with no credential.
    """
    patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
    entity_model = EntityModel.create_from_dict(
        {
            "businessIdentifier": COLIN_IDENTIFIER,
            "name": "NO PASSCODE LTD.",
            "corpTypeCode": "BC",
            "passCode": None,
            "isLoadedLear": False,
        }
    )
    entity = EntityService(entity_model)

    assert entity.pass_code is None
    assert AffiliationService.is_authorized(entity, None) is False


def test_lear_entity_without_passcode_keeps_existing_behaviour(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert the COLIN guard does not change how LEAR entities are authorized."""
    patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
    entity_model = EntityModel.create_from_dict(
        {
            "businessIdentifier": "BC1111111",
            "name": "LEAR COMPANY LTD.",
            "corpTypeCode": "BC",
            "passCode": None,
        }
    )
    entity = EntityService(entity_model)

    assert entity_model.is_loaded_lear is True
    assert AffiliationService.is_authorized(entity, None) is True


def test_colin_entity_authorized_with_correct_passcode(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert the synced COLIN passcode validates through the existing passcode flow."""
    patch_token_info(TestJwtClaims.public_user_role, monkeypatch)
    monkeypatch.setattr(ColinService, "fetch_auth_info", staticmethod(lambda _: _colin_info()))
    entity = EntityService.sync_from_colin(COLIN_IDENTIFIER)

    assert AffiliationService.is_authorized(entity, "111111111") is True
    assert AffiliationService.is_authorized(entity, "000000000") is False


def test_get_colin_affiliation_details(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert dashboard rows are built from auth data for businesses not in LEAR."""
    monkeypatch.setattr(ColinService, "fetch_auth_info", staticmethod(lambda _: _colin_info()))
    EntityService.sync_from_colin(COLIN_IDENTIFIER)

    search_details = AffiliationSearchDetails(page=1, limit=100)
    details = AffiliationService._get_colin_affiliation_details({COLIN_IDENTIFIER}, search_details)

    assert len(details) == 1
    assert details[0] == {
        "identifier": COLIN_IDENTIFIER,
        "legalName": "COLIN TEST COMPANY LTD.",
        "legalType": "BC",
        "state": "ACTIVE",
        "adminFreeze": False,
        "isLoadedLear": False,
    }


def test_get_colin_affiliation_details_applies_filters(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert search filters are applied locally, since LEAR cannot filter these."""
    monkeypatch.setattr(ColinService, "fetch_auth_info", staticmethod(lambda _: _colin_info()))
    EntityService.sync_from_colin(COLIN_IDENTIFIER)

    matching = AffiliationSearchDetails(page=1, limit=100, name="COLIN TEST")
    assert len(AffiliationService._get_colin_affiliation_details({COLIN_IDENTIFIER}, matching)) == 1

    non_matching = AffiliationSearchDetails(page=1, limit=100, name="SOMETHING ELSE")
    assert AffiliationService._get_colin_affiliation_details({COLIN_IDENTIFIER}, non_matching) == []

    wrong_status = AffiliationSearchDetails(page=1, limit=100, status=["HISTORICAL"])
    assert AffiliationService._get_colin_affiliation_details({COLIN_IDENTIFIER}, wrong_status) == []

    right_status = AffiliationSearchDetails(page=1, limit=100, status=["ACTIVE"])
    assert len(AffiliationService._get_colin_affiliation_details({COLIN_IDENTIFIER}, right_status)) == 1


def test_get_colin_affiliation_details_excludes_lear_entities(session):  # pylint:disable=unused-argument
    """Assert businesses loaded in LEAR are never served from the auth fallback."""
    EntityModel.create_from_dict(
        {
            "businessIdentifier": "BC2222222",
            "name": "LEAR COMPANY LTD.",
            "corpTypeCode": "BC",
            "passCode": passcode_hash("111111111"),
        }
    )

    search_details = AffiliationSearchDetails(page=1, limit=100)
    assert AffiliationService._get_colin_affiliation_details({"BC2222222"}, search_details) == []


def test_get_colin_identifiers_only_matches_unloaded_entities(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert identifier partitioning picks out only the COLIN businesses."""
    monkeypatch.setattr(ColinService, "fetch_auth_info", staticmethod(lambda _: _colin_info()))
    EntityService.sync_from_colin(COLIN_IDENTIFIER)
    EntityModel.create_from_dict(
        {
            "businessIdentifier": "BC3333333",
            "name": "LEAR COMPANY LTD.",
            "corpTypeCode": "BC",
            "passCode": None,
        }
    )

    result = AffiliationService._get_colin_identifiers([COLIN_IDENTIFIER, "BC3333333", "CP1234567", "NR 1234567"])

    assert result == {COLIN_IDENTIFIER}

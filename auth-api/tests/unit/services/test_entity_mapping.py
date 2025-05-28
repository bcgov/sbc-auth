"""Unit tests for the EntityMapping service."""

import pytest
from requests import HTTPError
from sqlalchemy import and_, or_

from auth_api.exceptions import BusinessException
from auth_api.models import db
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.dataclass import AffiliationSearchDetails
from auth_api.models.entity import Entity
from auth_api.models.entity_mapping import EntityMapping
from auth_api.models.org import Org as OrgModel
from auth_api.services.entity_mapping import EntityMappingService
from auth_api.services.rest_service import RestService
from tests.utilities.factory_utils import factory_org_service


@pytest.mark.parametrize(
    "test_name,entity_mapping_data,expected_count",
    [
        (
            "all_identifiers_present",
            # This payload comes straight from LEAR into the affiliation POST call.
            {"identifier": "BC5234567", "bootstrapIdentifier": "Txxxxxxxxx", "nrNumber": "NR5234567"},
            1,
        ),
        (
            "business_and_bootstrap_only",
            {"identifier": "BC5234567", "bootstrapIdentifier": "Txxxxxxxxx", "nrNumber": None},
            1,
        ),
        (
            "bootstrap_and_nr_only",
            {"identifier": None, "bootstrapIdentifier": "Txxxxxxxxx", "nrNumber": "NR5234567"},
            1,
        ),
        ("nr_only", {"identifier": None, "bootstrapIdentifier": None, "nrNumber": "NR5234567"}, 1),
        ("no_match", {"identifier": "DIFFERENT", "bootstrapIdentifier": "DIFFERENT", "nrNumber": "DIFFERENT"}, 0),
    ],
)
def test_get_filtered_affiliations_identifier_matches(session, test_name, entity_mapping_data, expected_count):
    """Test that affiliations are returned based on identifier matching logic."""
    service = EntityMappingService()
    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary["id"]

    entity1 = Entity(business_identifier="BC5234567", corp_type_code="BC").save()
    AffiliationModel(org_id=org_id, entity_id=entity1.id).save()
    entity2 = Entity(business_identifier="Txxxxxxxxx", corp_type_code="TMP").save()
    AffiliationModel(org_id=org_id, entity_id=entity2.id).save()
    entity3 = Entity(business_identifier="NR5234567", corp_type_code="NR").save()
    AffiliationModel(org_id=org_id, entity_id=entity3.id).save()

    service.from_entity_details(entity_mapping_data)

    search_details = AffiliationSearchDetails(page=1, limit=100)
    results = service.get_filtered_affiliations(org_id, search_details)

    assert len(results) == expected_count


@pytest.mark.parametrize(
    "test_name,identifiers,api_response,expected_mappings",
    [
        (
            "successful_population",
            ["BC1234567", "BC7654321"],
            [
                {"nrNumber": "NR1234567", "bootstrapIdentifier": "Txxxxxxxxx", "identifier": "BC1234567"},
                {"nrNumber": "NR7654321", "bootstrapIdentifier": "Tyyyyyyyy", "identifier": "BC7654321"},
            ],
            2,
        ),
        ("no_identifiers", [], [], 0),
        (
            "skip_existing_mappings",
            ["BC1234567", "BC7654321", "BC9999999"],
            [
                {"nrNumber": "NR1234567", "bootstrapIdentifier": "Txxxxxxxxx", "identifier": "BC1234567"},
                {"nrNumber": "NR7654321", "bootstrapIdentifier": "Tyyyyyyyy", "identifier": "BC7654321"},
                {"nrNumber": "NR9999999", "bootstrapIdentifier": "Tzzzzzzzz", "identifier": "BC9999999"},
            ],
            3,
        ),
        (
            "update_existing_mapping",
            ["BC1234567"],
            [{"nrNumber": "NR1234567", "bootstrapIdentifier": "Txxxxxxxxx", "identifier": "BC1234567"}],
            1,
        ),
    ],
)
def test_populate_entity_mappings(session, test_name, identifiers, api_response, expected_mappings, monkeypatch):
    """Test that populate_entity_mappings correctly fetches and populates entity mappings."""
    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary["id"]
    service = EntityMappingService()

    # Create entities and affiliations without mappings
    for identifier in identifiers:
        entity = Entity(business_identifier=identifier, corp_type_code="BC").save()
        AffiliationModel(org_id=org_id, entity_id=entity.id).save()

    # For the skip_existing_mappings test case, create a mapping for the third identifier
    if test_name == "skip_existing_mappings":
        EntityMapping(
            business_identifier="BC9999999", bootstrap_identifier="Tzzzzzzzz", nr_identifier="NR9999999"
        ).save()
    # For the update_existing_mapping test case, create a mapping with only nr_identifier
    elif test_name == "update_existing_mapping":
        EntityMapping(nr_identifier="NR1234567").save()

    monkeypatch.setattr(RestService, "get_service_account_token", lambda *args, **kwargs: {"accessToken": "mock_token"})
    monkeypatch.setattr(EntityMappingService, "fetch_entity_mappings_details", lambda *args, **kwargs: api_response)

    service.populate_entity_mappings(org_id)

    mappings = EntityMapping.query.all()
    assert len(mappings) == expected_mappings
    if expected_mappings > 0:
        mappings.sort(key=lambda x: x.business_identifier or "")
        for mapping, expected in zip(mappings, api_response):
            assert mapping.nr_identifier == expected["nrNumber"]
            assert mapping.bootstrap_identifier == expected["bootstrapIdentifier"]
            assert mapping.business_identifier == expected["identifier"]

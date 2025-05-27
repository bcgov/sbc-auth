"""Unit tests for the EntityMapping service."""

import pytest
from sqlalchemy import and_, or_

from auth_api.models import db
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.entity_mapping import EntityMapping
from auth_api.models.dataclass import AffiliationSearchDetails
from auth_api.models.entity import Entity
from auth_api.services.entity_mapping import EntityMappingService
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
def test_get_filtered_affiliations_identifier_matches(test_name, entity_mapping_data, expected_count):
    """Test that affiliations are returned based on identifier matching logic."""
    service = EntityMappingService(EntityMapping)
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

    # Clean up after this doesn't get reset in between these tests.
    db.session.query(AffiliationModel).delete()
    db.session.query(Entity).delete()
    db.session.query(EntityMapping).delete()
    db.session.commit()

    assert len(results) == expected_count

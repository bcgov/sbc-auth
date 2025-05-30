"""Unit tests for the EntityMapping service."""

from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.dataclass import AffiliationSearchDetails
from auth_api.models.entity import Entity
from auth_api.models.entity_mapping import EntityMapping
from auth_api.services.entity_mapping import EntityMappingService
from tests.utilities.factory_utils import factory_org_service


def test_get_filtered_affiliations_identifier_matches(session):
    """Test that affiliations are returned based on identifier matching logic."""

    entity_mapping_data = [
        # COLIN import - Business only on BRD
        {"identifier": "BC1234567", "bootstrapIdentifier": None, "nrNumber": None},
        # Numbered company draft - only temp identifier on BRD
        {"identifier": None, "bootstrapIdentifier": "Tyyyyyyy", "nrNumber": None},
        # NR - only nr identifier on BRD
        {"identifier": None, "bootstrapIdentifier": None, "nrNumber": "NR1234567"},
        # NR and TEMP (unconsumed) these should be combined into 1 row on the BRD,
        # but we need both entities to be considered 1 row for pagination
        {"identifier": None, "bootstrapIdentifier": "Taaaaaaa", "nrNumber": "NR1234561"},
        # Duplicate of above, considered 1 row for pagination
        {"identifier": None, "bootstrapIdentifier": "Tbbbbbbb", "nrNumber": "NR1234561"},
        # Normal named business flow - only business identifier - Skip rows for NR
        {"identifier": "BC7234567", "bootstrapIdentifier": "Txxxxxxx", "nrNumber": "NR1234565"},
        # Scenario where one TEMP has used the NR and completed the temp, the other TEMP just sits.
        {"identifier": "BC5234567", "bootstrapIdentifier": "Tiiiiiii", "nrNumber": "NR1235565"},
        {"identifier": None, "bootstrapIdentifier": "Tddddddd", "nrNumber": "NR1235565"},
        # Additional: Change of Name, I believe shows 2 rows and doesn't combine
    ]

    expected_before_search = [
        ["BC1234567"],
        ["Tyyyyyyy"],
        ["NR1234567"],
        ["Taaaaaaa", "NR1234561"],
        ["Tbbbbbbb", "NR1234561"],
        ["BC7234567"],
        ["BC5234567"],
        ["Tddddddd", "NR1235565"],
    ]

    service = EntityMappingService()
    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary["id"]

    # Reverse the list since results are ordered by created date DESC
    entity_mapping_data.reverse()
    for data in entity_mapping_data:
        _create_affiliations_for_mapping(session, org_id, data)

    for page in range(1, len(entity_mapping_data)):
        search_details = AffiliationSearchDetails(page=page, limit=1)
        results = service.paginage_from_affiliations(org_id, search_details)
        assert results[0][0] == expected_before_search[page - 1]


def _get_or_create_entity(session, business_identifier, corp_type_code):
    """Get existing entity or create a new one if it doesn't exist."""
    existing_entity = (
        session.query(Entity)
        .filter(Entity.business_identifier == business_identifier, Entity.corp_type_code == corp_type_code)
        .first()
    )

    return (
        existing_entity
        or Entity(business_identifier=business_identifier, corp_type_code=corp_type_code, is_loaded_lear=True).save()
    )


def _get_or_create_affiliation(session, org_id, entity_id):
    """Get existing affiliation or create a new one if it doesn't exist."""
    existing_affiliation = (
        session.query(AffiliationModel)
        .filter(AffiliationModel.org_id == org_id, AffiliationModel.entity_id == entity_id)
        .first()
    )

    return existing_affiliation or AffiliationModel(org_id=org_id, entity_id=entity_id).save()


def _create_affiliations_for_mapping(session, org_id, data):
    """Create an affiliation for each non-None value in the mapping data."""
    EntityMapping(
        business_identifier=data.get("identifier"),
        bootstrap_identifier=data.get("bootstrapIdentifier"),
        nr_identifier=data.get("nrNumber"),
    ).save()

    # Follows the business flow, NR always comes first
    if data.get("nrNumber"):
        entity = _get_or_create_entity(session, data["nrNumber"], "NR")
        _get_or_create_affiliation(session, org_id, entity.id)

    if data.get("bootstrapIdentifier"):
        entity = _get_or_create_entity(session, data["bootstrapIdentifier"], "TMP")
        _get_or_create_affiliation(session, org_id, entity.id)

    if data.get("identifier"):
        entity = _get_or_create_entity(session, data["identifier"], "BC")
        _get_or_create_affiliation(session, org_id, entity.id)

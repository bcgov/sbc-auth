"""Unit tests for the EntityMapping service."""

from unittest.mock import Mock, patch

from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.dataclass import AffiliationSearchDetails
from auth_api.models.entity import Entity
from auth_api.models.entity_mapping import EntityMapping
from auth_api.services.entity_mapping import EntityMappingService
from tests.utilities.factory_utils import factory_org_service


def _setup_orgs():
    """Set up test organizations."""
    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary["id"]

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    alternate_org_id = org_dictionary["id"]

    return org_id, alternate_org_id


def _get_or_create_entity(session, business_identifier, corp_type_code, is_loaded_lear=True):
    """Get existing entity or create a new one if it doesn't exist."""
    existing_entity = (
        session.query(Entity)
        .filter(Entity.business_identifier == business_identifier, Entity.corp_type_code == corp_type_code)
        .first()
    )

    return (
        existing_entity
        or Entity(
            business_identifier=business_identifier, corp_type_code=corp_type_code, is_loaded_lear=is_loaded_lear
        ).save()
    )


def _get_or_create_affiliation(session, org_id, entity_id):
    """Get existing affiliation or create a new one if it doesn't exist."""
    existing_affiliation = (
        session.query(AffiliationModel)
        .filter(AffiliationModel.org_id == org_id, AffiliationModel.entity_id == entity_id)
        .first()
    )

    return existing_affiliation or AffiliationModel(org_id=org_id, entity_id=entity_id).save()


def _create_affiliations_for_mapping(session, org_id, data, alternate_org_id, is_loaded_lear=True):
    """Create an affiliation for each non-None value in the mapping data."""
    EntityMapping(
        business_identifier=data.get("identifier"),
        bootstrap_identifier=data.get("bootstrapIdentifier"),
        nr_identifier=data.get("nrNumber"),
    ).save()

    # Follows the business flow, NR always comes first
    if data.get("nrNumber"):
        entity = _get_or_create_entity(session, data["nrNumber"], "NR", is_loaded_lear)
        _get_or_create_affiliation(session, alternate_org_id if "nrDifferentOrg" in data else org_id, entity.id)

    if data.get("bootstrapIdentifier"):
        entity = _get_or_create_entity(session, data["bootstrapIdentifier"], "TMP", is_loaded_lear)
        _get_or_create_affiliation(session, alternate_org_id if "bootstrapDifferentOrg" in data else org_id, entity.id)

    if data.get("identifier") and not data.get("identifierSkipAffiliationAndEntity"):
        entity = _get_or_create_entity(session, data["identifier"], "BC", is_loaded_lear)
        _get_or_create_affiliation(session, org_id, entity.id)


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
        # Scenario where one TEMP has used the NR and completed the temp, the other temps are hidden.
        {"identifier": None, "bootstrapIdentifier": "Teeeeeee", "nrNumber": "NR1235565"},
        {"identifier": "BC5234567", "bootstrapIdentifier": "Tiiiiiii", "nrNumber": "NR1235565"},
        {"identifier": None, "bootstrapIdentifier": "Tddddddd", "nrNumber": "NR1235565"},
        # Test cases with affiliations to different orgs
        # Business belongs to Org 1, Temp Org 1, NR Org 2 - Should Hide NR for Org 2
        # fix stale affiliations will repoint the NR to the business automatically
        {"identifier": "BC9999999", "bootstrapIdentifier": "T9999999", "nrNumber": "NR9999999", "nrDifferentOrg": True},
        # Business belongs to Org 1, NR belongs to Org 2 - should show Business for Org1, Org 2 should be hidden
        {"identifier": None, "bootstrapIdentifier": "T8888888", "nrNumber": "NR8888888", "nrDifferentOrg": True},
        # Test case with no entity or affiliation for the business identifier
        # But having an entity and affiliation for the bootstrap identifier
        # This should not show up in the results
        {
            "identifier": "BC9999993",
            "identifierSkipAffiliationAndEntity": True,
            "bootstrapIdentifier": "T7777777",
            "nrNumber": "NR7777777",
        },
        # NR case with Bootstrap, should be 1 row just the TEMP and NR, not TEMP+NR and NR for ORG1
        {
            "identifier": None,
            "bootstrapIdentifier": "Tazzzzza",
            "nrNumber": "NR7777775",
        },
        {
            "identifier": None,
            "bootstrapIdentifier": "Tzzzzzzd",
            "bootstrapDifferentOrg": True,
            "nrNumber": "NR7777775",
            "nrDifferentOrg": True,
        },
    ]

    expected_before_search_org_1 = [
        ["BC1234567"],
        ["Tyyyyyyy"],
        ["NR1234567"],
        ["Taaaaaaa", "NR1234561"],
        ["Tbbbbbbb", "NR1234561"],
        ["BC7234567"],
        ["BC5234567"],
        ["BC9999999"],
        ["T8888888"],
        ["Tazzzzza", "NR7777775"],
        [],
    ]

    # NR9999999 is not shown because it's turned into a business
    # the NR affiliation is typically repointed to the business - which is important the business affiliation
    # must exist to manage the business.
    expected_before_search_org_2 = [["NR8888888"], ["Tzzzzzzd", "NR7777775"]]
    service = EntityMappingService()
    org_id, alternate_org_id = _setup_orgs()

    # Reverse the list since results are ordered by created date DESC
    entity_mapping_data.reverse()
    for data in entity_mapping_data:
        _create_affiliations_for_mapping(session, org_id, data, alternate_org_id)

    search_details = AffiliationSearchDetails(page=1, limit=1000)
    results, _ = service.paginate_from_affiliations(org_id, search_details)

    actual_identifiers = [result[0] for result in results]
    expected_identifiers = [entry for entry in expected_before_search_org_1 if entry != []]
    assert actual_identifiers == expected_identifiers

    results, _ = service.paginate_from_affiliations(alternate_org_id, search_details)
    actual_identifiers = [result[0] for result in results]
    expected_identifiers = [entry for entry in expected_before_search_org_2 if entry != []]
    assert actual_identifiers == expected_identifiers


def test_from_entity_details_multiple_identifiers(session):
    """Test that from_entity_details correctly handles multiple identifiers and duplicate NRs."""
    service = EntityMappingService()
    service.from_entity_details(
        {"identifier": None, "bootstrapIdentifier": None, "nrNumber": "NR1234567"}, skip_auth=True
    )
    # Should skip this row, as it's a duplicate of the row above.
    service.from_entity_details({"nrNumber": "NR1234567"}, skip_auth=True)

    assert session.query(EntityMapping).order_by(EntityMapping.id).count() == 1

    service.from_entity_details(
        {"identifier": None, "bootstrapIdentifier": "T1234567", "nrNumber": "NR1234567"}, skip_auth=True
    )
    service.from_entity_details(
        {"identifier": None, "bootstrapIdentifier": "T7654321", "nrNumber": "NR1234567"}, skip_auth=True
    )
    service.from_entity_details(
        {"identifier": "BC1234567", "bootstrapIdentifier": "T1234567", "nrNumber": "NR1234567"}, skip_auth=True
    )
    service.from_entity_details(
        {"identifier": None, "bootstrapIdentifier": "T5234567", "nrNumber": None}, skip_auth=True
    )
    service.from_entity_details(
        {"identifier": "BC5234567", "bootstrapIdentifier": "T5234567", "nrNumber": None}, skip_auth=True
    )
    service.from_entity_details(
        {"identifier": "BC6234567", "bootstrapIdentifier": None, "nrNumber": None}, skip_auth=True
    )

    results = session.query(EntityMapping).order_by(EntityMapping.id).all()

    # Should have 4 distinct rows:
    # 1. NR+TMP+BC (updated from NR with TMP then BC)
    # 2. NR+TMP (new row with different TMP)
    # 3. TMP+BC (updated from TMP)
    # 4. BC only (new row)
    assert len(results) == 4
    assert results[0].business_identifier == "BC1234567"
    assert results[0].bootstrap_identifier == "T1234567"
    assert results[0].nr_identifier == "NR1234567"
    assert results[1].business_identifier is None
    assert results[1].bootstrap_identifier == "T7654321"
    assert results[1].nr_identifier == "NR1234567"
    assert results[2].business_identifier == "BC5234567"
    assert results[2].bootstrap_identifier == "T5234567"
    assert results[2].nr_identifier is None
    assert results[3].business_identifier == "BC6234567"
    assert results[3].bootstrap_identifier is None
    assert results[3].nr_identifier is None

    service.from_entity_details({"bootstrapIdentifier": "T5234562", "nrNumber": "NR1234563"}, skip_auth=True)
    service.from_entity_details({"bootstrapIdentifier": "T5234563", "nrNumber": "NR1234563"}, skip_auth=True)
    # Should only update the bootstrapIdentifier and nrNumber matching
    service.from_entity_details(
        {"identifier": "BC6534567", "bootstrapIdentifier": "T5234563", "nrNumber": "NR1234563"}, skip_auth=True
    )
    assert session.query(EntityMapping).order_by(EntityMapping.id).count() == 6
    results = (
        session.query(EntityMapping).order_by(EntityMapping.id).filter(EntityMapping.nr_identifier == "NR1234563").all()
    )
    assert len(results) == 2
    assert results[0].business_identifier is None
    assert results[1].business_identifier == "BC6534567"


def test_populate_entity_mapping_for_identifier_success(session):
    """Test successful population of entity mapping for identifier."""
    mock_entity_details = [{"nrNumber": "NR1234567", "bootstrapIdentifier": "TMP1234567", "identifier": "BC1234567"}]
    with patch.object(EntityMappingService, "fetch_entity_mapping_details", return_value=mock_entity_details):
        EntityMappingService.populate_entity_mapping_for_identifier("BC1234567")

        mapping = session.query(EntityMapping).first()
        assert mapping is not None
        assert mapping.nr_identifier == "NR1234567"
        assert mapping.bootstrap_identifier == "TMP1234567"
        assert mapping.business_identifier == "BC1234567"


def test_populate_entity_mapping_for_identifier_no_data(session):
    """Test that no entity mapping is created when no data is returned."""
    with patch.object(EntityMappingService, "fetch_entity_mapping_details", return_value=None):
        EntityMappingService.populate_entity_mapping_for_identifier("BC1234567")
        mapping = session.query(EntityMapping).first()
        assert mapping is None


def test_get_filtered_affiliations_identifier_matches_not_loaded_lear(session):
    """Test that affiliations are not returned when is_loaded_lear is False."""
    entity_mapping_data = [
        {"identifier": "BC1234567", "bootstrapIdentifier": None, "nrNumber": None},
        {"identifier": None, "bootstrapIdentifier": "Tyyyyyyy", "nrNumber": None},
        {"identifier": None, "bootstrapIdentifier": None, "nrNumber": "NR1234567"},
    ]

    service = EntityMappingService()
    org_id, _ = _setup_orgs()

    for data in entity_mapping_data:
        _create_affiliations_for_mapping(session, org_id, data, None, is_loaded_lear=False)

    search_details = AffiliationSearchDetails(page=1, limit=1000)
    results, _ = service.paginate_from_affiliations(org_id, search_details)

    assert len(results) == 0


def test_get_filtered_affiliations_pagination_limit_one(session):
    """Test pagination behavior with limit=1 and hasMore=true."""
    entity_mapping_data = [
        {"identifier": "BC1234567", "bootstrapIdentifier": None, "nrNumber": None},
        {"identifier": "BC1234568", "bootstrapIdentifier": None, "nrNumber": None},
        {"identifier": "BC1234569", "bootstrapIdentifier": None, "nrNumber": None},
    ]

    service = EntityMappingService()
    org_id, _ = _setup_orgs()

    for data in entity_mapping_data:
        _create_affiliations_for_mapping(session, org_id, data, None)

    search_details = AffiliationSearchDetails(page=1, limit=1)
    results, has_more = service.paginate_from_affiliations(org_id, search_details)

    assert len(results) == 1
    assert has_more is True
    assert results[0][0] == ["BC1234569"]

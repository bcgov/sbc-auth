# Copyright © 2025 Province of British Columbia
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
"""Tests for the auth_event_publisher utility.

Test suite to ensure that auth event publishing works correctly for unaffiliation
and team member ejection scenarios with multiple orgs, affiliations, and users.
"""

from unittest.mock import patch

import pytest
from sbc_common_components.utils.enums import QueueMessageTypes

from auth_api.utils.auth_event_publisher import (
    AccountEvent,
    UserAffiliationEvent,
    publish_affiliation_event,
    publish_team_member_event,
)
from tests.utilities.factory_utils import (
    factory_affiliation_model,
    factory_entity_model,
    factory_membership_model,
    factory_org_model,
    factory_user_model,
)


def _setup_orgs_entities_affiliations(num_orgs, num_affiliations_per_org):
    """Create orgs, entities, and affiliations for testing."""
    orgs = []
    entities = []
    affiliations = []

    for i in range(num_orgs):
        org = factory_org_model(org_info={"name": f"Org {i + 1}", "accessType": ""})
        orgs.append(org)
        for j in range(num_affiliations_per_org):
            entity = factory_entity_model(
                entity_info={
                    "businessIdentifier": f"BI{i + 1}-{j + 1}",
                    "businessNumber": f"BN{i + 1}-{j + 1}",
                    "name": f"Entity {i + 1}-{j + 1}",
                    "corpTypeCode": "BC",
                    "passCode": "",
                }
            )
            entities.append(entity)
            affiliations.append(factory_affiliation_model(entity.id, org.id))

    return orgs, entities, affiliations


def _setup_users_memberships(orgs, users_in_org1_only, users_in_both_orgs):
    """Create users and memberships for testing."""
    users_org1_only = []
    users_both_orgs = []

    for i in range(users_in_org1_only):
        user = factory_user_model(
            user_info={
                "username": f"user1_{i + 1}",
                "firstname": "User",
                "lastname": "One",
                "roles": "",
                "idp_userid": f"idp_{i + 1}",
            }
        )
        users_org1_only.append(user)
        factory_membership_model(user.id, orgs[0].id, member_status=1)

    for i in range(users_in_both_orgs):
        user = factory_user_model(
            user_info={
                "username": f"user2_{i + 1}",
                "firstname": "User",
                "lastname": "Both",
                "roles": "",
                "idp_userid": f"idp_both_{i + 1}",
            }
        )
        users_both_orgs.append(user)
        factory_membership_model(user.id, orgs[0].id, member_status=1)
        if len(orgs) > 1:
            factory_membership_model(user.id, orgs[1].id, member_status=1)

    return users_org1_only, users_both_orgs


def _setup_shared_business_identifier():
    """Create 2 orgs with one shared business identifier and one org1-only identifier."""
    org1 = factory_org_model(org_info={"name": "Org 1", "accessType": ""})
    org2 = factory_org_model(org_info={"name": "Org 2", "accessType": ""})

    entity_shared = factory_entity_model(
        entity_info={
            "businessIdentifier": "BI1-1",
            "businessNumber": "BN1-1",
            "name": "Entity Shared",
            "corpTypeCode": "BC",
            "passCode": "",
        }
    )
    entity_org1_only = factory_entity_model(
        entity_info={
            "businessIdentifier": "BI1-2",
            "businessNumber": "BN1-2",
            "name": "Entity Org1 Only",
            "corpTypeCode": "BC",
            "passCode": "",
        }
    )
    factory_affiliation_model(entity_shared.id, org1.id)
    factory_affiliation_model(entity_shared.id, org2.id)
    factory_affiliation_model(entity_org1_only.id, org1.id)

    return [org1, org2]


def _create_test_users(orgs):
    """Create ejected and unaffected users with memberships in all orgs."""
    ejected_user = factory_user_model(
        user_info={
            "username": "ejected_user",
            "firstname": "Ejected",
            "lastname": "User",
            "roles": "",
            "idp_userid": "idp_ejected",
        }
    )
    unaffected_user = factory_user_model(
        user_info={
            "username": "unaffected_user",
            "firstname": "Unaffected",
            "lastname": "User",
            "roles": "",
            "idp_userid": "idp_unaffected",
        }
    )

    for org in orgs:
        factory_membership_model(ejected_user.id, org.id, member_status=1)
        factory_membership_model(unaffected_user.id, org.id, member_status=1)

    return ejected_user, unaffected_user


def _create_business_entity(business_identifier, business_number, name, corp_type_code="BC"):
    """Create a business entity for testing."""
    return factory_entity_model(
        entity_info={
            "businessIdentifier": business_identifier,
            "businessNumber": business_number,
            "name": name,
            "corpTypeCode": corp_type_code,
            "passCode": "",
        }
    )


def _create_test_user(username, idp_userid):
    """Create a test user with standard info."""
    return factory_user_model(
        user_info={
            "username": username,
            "firstname": "User",
            "lastname": username.split("_")[-1].title(),
            "roles": "",
            "idp_userid": idp_userid,
        }
    )


def _publish_and_get_account_event(mock_publish_account_event, org_id, business_identifier, should_publish=True):
    """Publish affiliation event and return the account event from the mock."""
    publish_affiliation_event(QueueMessageTypes.BUSINESS_UNAFFILIATED.value, org_id, business_identifier)

    if should_publish:
        mock_publish_account_event.assert_called_once()
        call_args = mock_publish_account_event.call_args

        assert call_args.kwargs["queue_message_type"] == QueueMessageTypes.BUSINESS_UNAFFILIATED.value
        account_event = call_args.kwargs["data"]

        return account_event
    else:
        mock_publish_account_event.assert_not_called()
        return None


def _assert_account_event(account_event, account_id, business_identifier, actioned_by):
    """Assert common account event properties."""
    assert isinstance(account_event, AccountEvent)
    assert account_event.account_id == account_id
    assert account_event.business_identifier == business_identifier
    assert account_event.actioned_by == actioned_by
    assert account_event.action_category == "account-management"


def _setup_unaffiliation_scenario(scenario_name):
    """Set up test data for different unaffiliation scenarios."""
    if scenario_name == "user_has_access_through_other_org":
        org1 = factory_org_model(org_info={"name": "Org 1", "accessType": ""})
        org2 = factory_org_model(org_info={"name": "Org 2", "accessType": ""})
        org3 = factory_org_model(org_info={"name": "Org 3", "accessType": ""})

        business1 = _create_business_entity("BI1", "BN1", "Business 1")
        business2 = _create_business_entity("BI2", "BN2", "Business 2")

        factory_affiliation_model(business1.id, org1.id)
        factory_affiliation_model(business2.id, org2.id)
        factory_affiliation_model(business1.id, org3.id)

        user1 = _create_test_user("user1", "idp_user1")
        factory_membership_model(user1.id, org1.id, member_status=1)
        factory_membership_model(user1.id, org2.id, member_status=1)
        factory_membership_model(user1.id, org3.id, member_status=1)

        return org1, business1.business_identifier, [], []

    elif scenario_name == "multiple_users_one_loses_access":
        org1 = factory_org_model(org_info={"name": "Org 1", "accessType": ""})
        org2 = factory_org_model(org_info={"name": "Org 2", "accessType": ""})

        business1 = _create_business_entity("BI1", "BN1", "Business 1")

        factory_affiliation_model(business1.id, org1.id)
        factory_affiliation_model(business1.id, org2.id)

        user1 = _create_test_user("user1", "idp_user1")
        user2 = _create_test_user("user2", "idp_user2")

        factory_membership_model(user1.id, org1.id, member_status=1)
        factory_membership_model(user1.id, org2.id, member_status=1)
        factory_membership_model(user2.id, org1.id, member_status=1)

        return org1, business1.business_identifier, ["idp_user2"], ["idp_user1"]

    elif scenario_name == "both_users_lose_access":
        org1 = factory_org_model(org_info={"name": "Org 1", "accessType": ""})
        org2 = factory_org_model(org_info={"name": "Org 2", "accessType": ""})

        business1 = _create_business_entity("BI1", "BN1", "Business 1")
        business2 = _create_business_entity("BI2", "BN2", "Business 2")

        factory_affiliation_model(business1.id, org1.id)
        factory_affiliation_model(business2.id, org2.id)

        user1 = _create_test_user("user1", "idp_user1")
        user2 = _create_test_user("user2", "idp_user2")

        factory_membership_model(user1.id, org2.id, member_status=1)
        factory_membership_model(user2.id, org2.id, member_status=1)

        return org2, business2.business_identifier, ["idp_user1", "idp_user2"], []

    elif scenario_name == "nr_business_identifier":
        org1 = factory_org_model(org_info={"name": "Org 1", "accessType": ""})
        org2 = factory_org_model(org_info={"name": "Org 2", "accessType": ""})

        nr_business = _create_business_entity("NR 1234567", "BN1", "ABC Corp Inc.")

        factory_affiliation_model(nr_business.id, org1.id)
        factory_affiliation_model(nr_business.id, org2.id)

        user1 = _create_test_user("user1", "idp_user1")
        user2 = _create_test_user("user2", "idp_user2")

        factory_membership_model(user1.id, org1.id, member_status=1)
        factory_membership_model(user1.id, org2.id, member_status=1)
        factory_membership_model(user2.id, org1.id, member_status=1)

        return org1, nr_business.business_identifier, ["idp_user2"], ["idp_user1"]

    elif scenario_name == "tmp_business_identifier":
        org1 = factory_org_model(org_info={"name": "Org 1", "accessType": ""})
        org2 = factory_org_model(org_info={"name": "Org 2", "accessType": ""})

        tmp_business = _create_business_entity("T1234567", "BN1", "NR 1234567")

        factory_affiliation_model(tmp_business.id, org1.id)
        factory_affiliation_model(tmp_business.id, org2.id)

        user1 = _create_test_user("user1", "idp_user1")
        user2 = _create_test_user("user2", "idp_user2")

        factory_membership_model(user1.id, org1.id, member_status=1)
        factory_membership_model(user1.id, org2.id, member_status=1)
        factory_membership_model(user2.id, org1.id, member_status=1)

        return org1, tmp_business.business_identifier, ["idp_user2"], ["idp_user1"]

    raise ValueError(f"Unknown scenario: {scenario_name}")


@pytest.mark.parametrize(
    "scenario_name, expected_user_ids, expected_no_event_user_ids, should_publish",
    [
        ("user_has_access_through_other_org", [], [], True),
        ("multiple_users_one_loses_access", ["idp_user2"], ["idp_user1"], True),
        ("both_users_lose_access", ["idp_user1", "idp_user2"], [], True),
        ("nr_business_identifier", [], [], False),
        ("tmp_business_identifier", [], [], False),
    ],
    ids=[
        "user_has_access_through_other_org",
        "multiple_users_one_loses_access",
        "both_users_lose_access",
        "nr_business_identifier",
        "tmp_business_identifier",
    ],
)
@patch("auth_api.utils.auth_event_publisher.publish_account_event")
@patch("auth_api.utils.auth_event_publisher._get_actioned_by")
def test_publish_affiliation_event_unaffiliation(
    mock_get_actioned_by,
    mock_publish_account_event,
    session,  # pylint:disable=unused-argument
    scenario_name,
    expected_user_ids,
    expected_no_event_user_ids,
    should_publish,
):
    """Test publish_affiliation_event for unaffiliation with various scenarios."""
    mock_get_actioned_by.return_value = "test_user_123"

    target_org, target_business_identifier, _expected_ids, _no_event_ids = _setup_unaffiliation_scenario(scenario_name)

    account_event = _publish_and_get_account_event(
        mock_publish_account_event, target_org.id, target_business_identifier, should_publish
    )

    if should_publish:
        _assert_account_event(account_event, target_org.id, target_business_identifier, "test_user_123")

        assert len(account_event.user_affiliation_events) == len(expected_user_ids)

        if expected_user_ids:
            user_ids = [event.idp_userid for event in account_event.user_affiliation_events]
            for expected_id in expected_user_ids:
                assert expected_id in user_ids

            for user_event in account_event.user_affiliation_events:
                assert isinstance(user_event, UserAffiliationEvent)
                assert user_event.unaffiliated_identifiers == [target_business_identifier]

        if expected_no_event_user_ids:
            event_user_ids = [event.idp_userid for event in account_event.user_affiliation_events]
            for no_event_id in expected_no_event_user_ids:
                assert no_event_id not in event_user_ids


def _setup_nr_business_identifier():
    """Create 2 orgs with NR business identifier affiliations."""
    org1 = factory_org_model(org_info={"name": "Org 1", "accessType": ""})
    org2 = factory_org_model(org_info={"name": "Org 2", "accessType": ""})

    nr_entity = _create_business_entity("NR 1234567", "BN1", "ABC Corp Inc.", "NR")
    factory_affiliation_model(nr_entity.id, org1.id)
    factory_affiliation_model(nr_entity.id, org2.id)

    return [org1, org2]


def _setup_tmp_business_identifier():
    """Create 2 orgs with TMP business identifier affiliations."""
    org1 = factory_org_model(org_info={"name": "Org 1", "accessType": ""})
    org2 = factory_org_model(org_info={"name": "Org 2", "accessType": ""})

    tmp_entity = _create_business_entity("QWERTYUIO", "BN1", "NR 1234567", "TMP")
    factory_affiliation_model(tmp_entity.id, org1.id)
    factory_affiliation_model(tmp_entity.id, org2.id)

    return [org1, org2]


@pytest.mark.parametrize(
    "use_shared_setup, expected_user_affiliation_event, should_publish",
    [
        (False, {"idp_userid": "idp_ejected", "unaffiliated_identifiers": ["BI1-1", "BI1-2"]}, True),
        (True, {"idp_userid": "idp_ejected", "unaffiliated_identifiers": ["BI1-2"]}, True),
        ("nr", None, False),
        ("tmp", None, False),
    ],
    ids=[
        "two_orgs_2_affiliations_each_org",
        "two_orgs_3_affiliations_only_1_unaffiliated",
        "nr_business_identifier",
        "tmp_business_identifier",
    ],
)
@patch("auth_api.utils.auth_event_publisher.publish_account_event")
@patch("auth_api.utils.auth_event_publisher._get_actioned_by")
def test_publish_team_member_event_ejection(
    mock_get_actioned_by,
    mock_publish_account_event,
    session,  # pylint:disable=unused-argument
    use_shared_setup,
    expected_user_affiliation_event,
    should_publish,
):
    """Test publish_team_member_event for team member ejection with various org/affiliation scenarios."""
    mock_get_actioned_by.return_value = "test_user_123"

    if use_shared_setup == "nr":
        orgs = _setup_nr_business_identifier()
    elif use_shared_setup == "tmp":
        orgs = _setup_tmp_business_identifier()
    elif use_shared_setup:
        orgs = _setup_shared_business_identifier()
    else:
        orgs, _entities, _affiliations = _setup_orgs_entities_affiliations(2, 2)

    target_org = orgs[0]
    ejected_user, unaffected_user = _create_test_users(orgs)

    publish_team_member_event(QueueMessageTypes.TEAM_MEMBER_REMOVED.value, target_org.id, ejected_user.id)

    if should_publish:
        mock_publish_account_event.assert_called_once()
        call_args = mock_publish_account_event.call_args

        assert call_args.kwargs["queue_message_type"] == QueueMessageTypes.TEAM_MEMBER_REMOVED.value
        account_event = call_args.kwargs["data"]

        _assert_account_event(account_event, target_org.id, None, "test_user_123")

        assert len(account_event.user_affiliation_events) == 1
        user_event = account_event.user_affiliation_events[0]

        assert isinstance(user_event, UserAffiliationEvent)
        assert user_event.idp_userid == expected_user_affiliation_event["idp_userid"]
        assert user_event.login_source == ejected_user.login_source
        assert set(user_event.unaffiliated_identifiers) == set(
            expected_user_affiliation_event["unaffiliated_identifiers"]
        )
        assert unaffected_user.idp_userid not in [event.idp_userid for event in account_event.user_affiliation_events]
    else:
        mock_publish_account_event.assert_not_called()


def test_account_event_to_dict_camelcase_serialization():
    """Test that AccountEvent.to_dict() serializes unaffiliated_identifiers to camelCase."""
    user_event = UserAffiliationEvent(
        idp_userid="test_user_123",
        login_source="BCSC",
        unaffiliated_identifiers=["BI1", "BI2", "BI3"],
    )

    account_event = AccountEvent(
        account_id=123,
        actioned_by="admin_user",
        business_identifier="BI1",
        user_affiliation_events=[user_event],
    )

    serialized = account_event.to_dict()

    assert "unaffiliatedIdentifiers" in serialized["userAffiliationEvents"][0]
    assert serialized["userAffiliationEvents"][0]["unaffiliatedIdentifiers"] == ["BI1", "BI2", "BI3"]
    assert "unaffiliated_identifiers" not in serialized["userAffiliationEvents"][0]

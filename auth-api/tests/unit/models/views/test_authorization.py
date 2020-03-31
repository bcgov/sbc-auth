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
"""Tests for the Authorizations view.

Test suite to ensure that the Authorizations view routines are working as expected.
"""
import uuid

from auth_api.models.views.authorization import Authorization
from tests.utilities.factory_scenarios import TestUserInfo
from tests.utilities.factory_utils import (
    factory_affiliation_model, factory_entity_model, factory_membership_model, factory_org_model, factory_user_model)


def test_find_user_authorization_by_business_number(session):  # pylint:disable=unused-argument
    """Assert that authorization view is returning result."""
    user = factory_user_model()
    org = factory_org_model()
    membership = factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    authorization = Authorization.find_user_authorization_by_business_number(entity.business_identifier,
                                                                             str(user.keycloak_guid))

    assert authorization is not None
    assert authorization.org_membership == membership.membership_type_code


def test_find_user_authorization_by_org_id(session):  # pylint:disable=unused-argument
    """Assert that authorization view is returning result."""
    user = factory_user_model()
    org = factory_org_model()
    membership = factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    authorization = Authorization.find_user_authorization_by_org_id(str(user.keycloak_guid),
                                                                    org.id)

    assert authorization is not None
    assert authorization.org_membership == membership.membership_type_code


def test_find_user_authorization_by_org_id_and_corp_type(session):  # pylint:disable=unused-argument
    """Assert that authorization view returns result when fetched using Corp type instead of jwt.

    Service accounts passes corp type instead of jwt.
    """
    user = factory_user_model()
    org = factory_org_model()
    membership = factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    authorization = Authorization.find_user_authorization_by_org_id_and_corp_type(org.id, 'CP')

    assert authorization is not None
    assert authorization.org_membership == membership.membership_type_code


def test_find_user_authorization_by_org_id_and_corp_type_multiple_membership(session):  # pylint:disable=unused-argument
    """Assert that authorization view returns result when fetched using Corp type instead of jwt.

    When multiple membership is present , return the one with Owner access.
    """
    user1 = factory_user_model()
    user2 = factory_user_model(user_info=TestUserInfo.user2)
    org = factory_org_model()
    factory_membership_model(user1.id, org.id, member_type='ADMIN')
    membership_owner = factory_membership_model(user2.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    authorization = Authorization.find_user_authorization_by_org_id_and_corp_type(org.id, 'CP')

    assert authorization is not None
    assert authorization.org_membership == membership_owner.membership_type_code


def test_find_user_authorization_by_business_number_and_corp_type_multiple_membership(
        session):  # pylint:disable=unused-argument
    """Assert that authorization view returns result when fetched using Corp type instead of jwt.

    When multiple membership is present , return the one with Owner access
    """
    user1 = factory_user_model()
    user2 = factory_user_model(user_info=TestUserInfo.user2)
    org = factory_org_model()
    factory_membership_model(user1.id, org.id, member_type='ADMIN')
    membership_owner = factory_membership_model(user2.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    authorization = Authorization.find_user_authorization_by_business_number_and_corp_type(entity.business_identifier,
                                                                                           'CP')

    assert authorization is not None
    assert authorization.org_membership == membership_owner.membership_type_code


def test_find_user_authorization_by_org_id_and_invalid_corp_type(session):  # pylint:disable=unused-argument
    """Assert that authorization view is not returning result when invalid corp type is passed."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    authorization = Authorization.find_user_authorization_by_org_id_and_corp_type(org.id, 'invalid_corp_type')

    assert authorization is None


def test_find_user_authorization_by_org_id_and_invalid_corp_type_no_affliation(
        session):  # pylint:disable=unused-argument # noqa: E501
    """Assert that authorization view is returning correct result for an unclaimed/unaffiliated organization."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    authorization = Authorization.find_user_authorization_by_org_id_and_corp_type(org.id, 'invalid_corp_type')
    assert authorization is not None


def test_find_user_authorization_by_business_number_and_corp_type(session):  # pylint:disable=unused-argument
    """Assert that authorization view returns result when fetched using Corp type instead of jwt.

    Service accounts passes corp type instead of jwt.
    """
    user = factory_user_model()
    org = factory_org_model()
    membership = factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    authorization = Authorization.find_user_authorization_by_business_number_and_corp_type(entity.business_identifier,
                                                                                           'CP')

    assert authorization is not None
    assert authorization.org_membership == membership.membership_type_code


def test_find_user_authorization_by_business_number_and_invalid_corp_type(session):  # pylint:disable=unused-argument
    """Assert that authorization view is not returning result when invalid corp type is passed."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    authorization = Authorization.find_user_authorization_by_business_number_and_corp_type(entity.business_identifier,
                                                                                           'invalid_corp_type')

    assert authorization is None


def test_find_invalid_user_authorization_by_business_number(session):  # pylint:disable=unused-argument
    """Test with invalid user id and assert that auth is None."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    authorization = Authorization.find_user_authorization_by_business_number(entity.business_identifier,
                                                                             str(uuid.uuid4()))
    assert authorization is None

    # Test with invalid business identifier
    authorization = Authorization.find_user_authorization_by_business_number('', str(uuid.uuid4()))
    assert authorization is None


def test_find_all_user_authorizations(session):  # pylint:disable=unused-argument
    """Test find all user authoirzations."""
    user = factory_user_model()
    org = factory_org_model()
    membership = factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    authorizations = Authorization.find_all_authorizations_for_user(str(user.keycloak_guid))
    assert authorizations is not None
    assert authorizations[0].org_membership == membership.membership_type_code
    assert authorizations[0].business_identifier == entity.business_identifier


def test_find_all_user_authorizations_for_empty(session):  # pylint:disable=unused-argument
    """Test with invalid user id and assert that auth is None."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)

    authorizations = Authorization.find_all_authorizations_for_user(str(user.keycloak_guid))
    assert authorizations is not None
    assert authorizations[0].business_identifier is None

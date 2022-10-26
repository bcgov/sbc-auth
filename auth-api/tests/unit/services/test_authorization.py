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
"""Tests for the Authorization service.

Test suite to ensure that the Authorization service routines are working as expected.
"""

import uuid

import pytest
from werkzeug.exceptions import HTTPException

from auth_api.services.authorization import Authorization, check_auth
from auth_api.utils.enums import ProductCode
from auth_api.utils.roles import ADMIN, STAFF, USER
from tests.utilities.factory_scenarios import TestJwtClaims, TestUserInfo
from tests.utilities.factory_utils import (
    TestOrgInfo, TestOrgTypeInfo, factory_affiliation_model, factory_entity_model, factory_membership_model,
    factory_org_model, factory_product_model, factory_user_model, patch_token_info)


def test_get_user_authorizations_for_entity(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that user authorizations for entity is working."""
    user = factory_user_model()
    org = factory_org_model()
    membership = factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    patch_token_info({
        'sub': str(user.keycloak_guid),
        'realm_access': {
            'roles': ['basic']
        }}, monkeypatch)
    authorization = Authorization.get_user_authorizations_for_entity(entity.business_identifier)
    assert authorization is not None
    assert authorization.get('orgMembership', None) == membership.membership_type_code

    # Test with invalid user
    patch_token_info({'sub': str(uuid.uuid4()), 'realm_access': {
        'roles': ['basic']
    }}, monkeypatch)
    authorization = Authorization.get_user_authorizations_for_entity(entity.business_identifier)
    assert authorization is not None
    assert authorization.get('orgMembership', None) is None

    # Test for passcode users with invalid username
    patch_token_info({'loginSource': 'PASSCODE', 'username': 'INVALID', 'realm_access': {
        'roles': ['basic']
    }}, monkeypatch)
    authorization = Authorization.get_user_authorizations_for_entity(entity.business_identifier)

    assert authorization is not None
    assert authorization.get('orgMembership', None) is None

    # Test for staff users
    patch_token_info(
        {'loginSource': '', 'realm_access': {'roles': ['staff']}},
        monkeypatch)
    authorization = Authorization.get_user_authorizations_for_entity(entity.business_identifier)

    assert authorization is not None
    assert authorization.get('orgMembership', None) is None

    # test with api_gw source user
    patch_token_info({
        'Account-Id': org.id,
        'loginSource': 'API_GW',
        'sub': str(user.keycloak_guid),
        'realm_access': {
            'roles': ['basic']
        }}, monkeypatch)
    authorization = Authorization.get_user_authorizations_for_entity(entity.business_identifier)
    assert authorization is not None
    assert authorization.get('orgMembership', None) == membership.membership_type_code


def test_get_user_authorizations_for_org(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that user authorizations for entity is working."""
    user = factory_user_model()
    org = factory_org_model()
    membership = factory_membership_model(user.id, org.id)

    patch_token_info({
        'sub': str(user.keycloak_guid),
        'realm_access': {
            'roles': ['basic']
        }}, monkeypatch)
    authorization = Authorization.get_account_authorizations_for_org(org.id, ProductCode.BUSINESS.value)
    assert authorization is not None
    assert authorization.get('orgMembership', None) == membership.membership_type_code
    assert authorization.get('roles') is not None

    patch_token_info({
        'sub': str(user.keycloak_guid),
        'realm_access': {
            'roles': ['basic']
        }}, monkeypatch)
    authorization = Authorization.get_account_authorizations_for_org(org.id, ProductCode.NAMES_REQUEST.value)
    assert authorization is not None
    assert authorization.get('orgMembership', None) == membership.membership_type_code
    assert authorization.get('roles') is not None

    patch_token_info({
        'sub': str(user.keycloak_guid),
        'realm_access': {
            'roles': ['basic']
        }}, monkeypatch)
    authorization = Authorization.get_account_authorizations_for_org(org.id, ProductCode.VS.value)
    assert authorization is not None
    assert authorization.get('orgMembership') is None
    assert len(authorization.get('roles')) == 0


def test_get_user_authorizations_for_entity_service_account(session, monkeypatch):
    """Assert that user authorizations for entity is working."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id, product_code=ProductCode.BUSINESS.value)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    # Test for service accounts with correct product code
    patch_token_info(
        {'loginSource': '', 'realm_access': {'roles': ['system']}, 'product_code': ProductCode.BUSINESS.value},
        monkeypatch)
    authorization = Authorization.get_user_authorizations_for_entity(entity.business_identifier)
    assert bool(authorization) is True
    assert authorization.get('orgMembership', None) == 'ADMIN'

    # Test for service accounts with wrong product code
    patch_token_info({'loginSource': '', 'realm_access': {'roles': ['system']}, 'product_code': 'INVALIDCP'},
                     monkeypatch)
    authorization = Authorization.get_user_authorizations_for_entity(entity.business_identifier)
    assert bool(authorization) is False
    assert authorization.get('orgMembership', None) is None

    # Test for service accounts with no product code
    patch_token_info({'loginSource': '', 'realm_access': {'roles': ['system']}}, monkeypatch)
    authorization = Authorization.get_user_authorizations_for_entity(entity.business_identifier)
    assert bool(authorization) is False
    assert authorization.get('orgMembership', None) is None


def test_get_user_authorizations(session):  # pylint:disable=unused-argument
    """Assert that listing all user authorizations is working."""
    user = factory_user_model()
    org = factory_org_model()
    membership = factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    authorization = Authorization.get_user_authorizations(str(user.keycloak_guid))
    assert authorization is not None
    assert authorization['authorizations'][0].get('orgMembership', None) == membership.membership_type_code

    # Test with invalid user
    authorization = Authorization.get_user_authorizations(str(uuid.uuid4()))
    assert authorization is not None
    assert len(authorization['authorizations']) == 0


def test_check_auth(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that check_auth is working as expected."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id, product_code=ProductCode.BUSINESS.value)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    # Test if staff admin can access to STAFF only method
    patch_token_info({'realm_access': {'roles': ['staff', 'create_accounts']}, 'sub': str(user.keycloak_guid)},
                     monkeypatch)
    check_auth(one_of_roles=[STAFF])

    # Test for staff admin role to only STAFF
    patch_token_info({'realm_access': {'roles': ['staff', 'create_accounts']}, 'sub': str(user.keycloak_guid)},
                     monkeypatch)
    check_auth(equals_role=STAFF)

    # Test for staff role
    patch_token_info({'realm_access': {'roles': ['staff']}, 'sub': str(user.keycloak_guid),
                      'product_code': ProductCode.BUSINESS.value}, monkeypatch)
    check_auth(one_of_roles=[STAFF])
    # Test for owner role
    patch_token_info({'realm_access': {'roles': ['public']}, 'sub': str(user.keycloak_guid),
                      'product_code': ProductCode.BUSINESS.value}, monkeypatch)
    check_auth(one_of_roles=[ADMIN], business_identifier=entity.business_identifier)
    # Test for owner role with org id
    patch_token_info({'realm_access': {'roles': ['public']}, 'sub': str(user.keycloak_guid),
                      'product_code': ProductCode.BUSINESS.value}, monkeypatch)
    check_auth(one_of_roles=[ADMIN], org_id=org.id)

    # Test for exception, check for auth if resource is available for STAFF users
    with pytest.raises(HTTPException) as excinfo:
        patch_token_info({'realm_access': {'roles': ['public']}, 'sub': str(user.keycloak_guid)}, monkeypatch)
        check_auth(one_of_roles=[STAFF], business_identifier=entity.business_identifier)
        assert excinfo.exception.code == 403

    # Test auth where STAFF role is in disabled role list
    with pytest.raises(HTTPException) as excinfo:
        patch_token_info({'realm_access': {'roles': ['staff']}, 'sub': str(user.keycloak_guid)}, monkeypatch)
        check_auth(disabled_roles=[STAFF], business_identifier=entity.business_identifier)
        assert excinfo.exception.code == 403

    # Test auth where STAFF role is exact match
    with pytest.raises(HTTPException) as excinfo:
        patch_token_info({'realm_access': {'roles': ['public']}, 'sub': str(user.keycloak_guid)}, monkeypatch)
        check_auth(equals_role=USER, business_identifier=entity.business_identifier)
        assert excinfo.exception.code == 403

    # Test auth where STAFF role is exact match
    with pytest.raises(HTTPException) as excinfo:
        patch_token_info({'realm_access': {'roles': ['public']}, 'sub': str(user.keycloak_guid)}, monkeypatch)
        check_auth(equals_role=USER, org_id=org.id)
        assert excinfo.exception.code == 403

        # Test auth where STAFF role is exact match
        with pytest.raises(HTTPException) as excinfo:
            patch_token_info({'realm_access': {'roles': ['staff', 'create_accounts']}, 'sub': str(user.keycloak_guid)},
                             monkeypatch)
            check_auth(equals_role=USER, org_id=org.id)
            assert excinfo.exception.code == 403


def test_check_auth_for_service_account_valid_with_org_id(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that check_auth is working as expected."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id, product_code=ProductCode.BUSINESS.value)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    # Test for service account with CP corp type
    patch_token_info({'realm_access': {'roles': ['system']}, 'product_code': ProductCode.BUSINESS.value}, monkeypatch)
    check_auth(org_id=org.id)


def test_check_auth_for_service_account_valid_with_business_id(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that check_auth is working as expected."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id, product_code=ProductCode.BUSINESS.value)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    # Test for service account with CP corp type
    patch_token_info({'realm_access': {'roles': ['system']}, 'product_code': ProductCode.BUSINESS.value}, monkeypatch)
    check_auth(business_identifier=entity.business_identifier)


@pytest.mark.skip(reason='the approach changed;should be fixed later')
def test_check_auth_for_service_account_invalid(session):  # pylint:disable=unused-argument
    """Assert that check_auth is working as expected and throws exception."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    # Test for invalid CP
    # with pytest.raises(HTTPException) as excinfo:
    #    check_auth({'realm_access': {'roles': ['system']}, 'corp_type': 'IVALIDCP'}, org_id=org.id)
    #    assert excinfo.exception.code == 403

    # Test for invalid CP
    # with pytest.raises(HTTPException) as excinfo:
    #    check_auth({'realm_access': {'roles': ['system']}}, org_id=org.id)
    #    assert excinfo.exception.code == 403

    # Test for invalid CP with no args
    # with pytest.raises(HTTPException) as excinfo:
    #    check_auth({'realm_access': {'roles': ['system']}})
    #    assert excinfo.exception.code == 403


def test_get_account_authorizations_for_product(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that user authorizations for product is working."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)

    patch_token_info(TestJwtClaims.get_test_real_user(user.keycloak_guid), monkeypatch)
    authorization = Authorization.get_account_authorizations_for_product(org.id, 'PPR')
    assert authorization is not None
    assert len(authorization.get('roles')) == 0

    # Now add some product subscription for the org
    patch_token_info(TestJwtClaims.get_test_real_user(user.keycloak_guid), monkeypatch)
    factory_product_model(org.id)
    authorization = Authorization.get_account_authorizations_for_product(org.id, 'PPR')
    assert authorization is not None
    assert len(authorization.get('roles')) > 0

    # Create another org and assert that the roles are empty
    org = factory_org_model(org_info=TestOrgInfo.org2, org_type_info=TestOrgTypeInfo.implicit)
    factory_membership_model(user.id, org.id)
    patch_token_info(TestJwtClaims.get_test_real_user(user.keycloak_guid), monkeypatch)
    authorization = Authorization.get_account_authorizations_for_product(org.id, 'PPR')
    assert authorization is not None
    assert len(authorization.get('roles')) == 0

    factory_product_model(org.id)
    patch_token_info(TestJwtClaims.get_test_real_user(user.keycloak_guid), monkeypatch)
    authorization = Authorization.get_account_authorizations_for_product(org.id, 'PPR')
    assert authorization is not None
    assert len(authorization.get('roles')) > 0


def test_get_user_authorizations_for_entity_with_multiple_affiliations(session,  # pylint:disable=unused-argument
                                                                       monkeypatch):
    """Assert that user authorizations for entity is working."""
    user = factory_user_model()
    org = factory_org_model()
    membership = factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)
    patch_token_info({
        'sub': str(user.keycloak_guid),
        'realm_access': {
            'roles': ['basic']
        }}, monkeypatch)
    authorization = Authorization.get_user_authorizations_for_entity(entity.business_identifier)
    assert authorization is not None
    assert authorization.get('orgMembership', None) == membership.membership_type_code

    # Affiliate same entity to another org and user, and assert both authorizations works
    user_2 = factory_user_model(user_info=TestUserInfo.user2)
    org_2 = factory_org_model(org_info=TestOrgInfo.org2)
    membership = factory_membership_model(user_2.id, org_2.id)
    factory_affiliation_model(entity.id, org_2.id)
    patch_token_info({
        'sub': str(user_2.keycloak_guid),
        'realm_access': {
            'roles': ['basic']
        }}, monkeypatch)
    authorization = Authorization.get_user_authorizations_for_entity(entity.business_identifier)
    assert authorization is not None
    assert authorization.get('orgMembership', None) == membership.membership_type_code

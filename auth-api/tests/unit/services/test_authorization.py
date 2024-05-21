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
from contextlib import nullcontext as does_not_raise

import pytest
from werkzeug.exceptions import Forbidden, HTTPException

from auth_api.services.authorization import Authorization, check_auth
from auth_api.utils.enums import ProductCode
from auth_api.utils.roles import ADMIN, STAFF, USER
from tests.utilities.factory_scenarios import TestEntityInfo, TestJwtClaims, TestUserInfo
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


@pytest.mark.parametrize(
    'test_desc,test_expect,additional_kwargs,add_org_id',
    [
        ('Test 403 when no role checks provided in kwargs.', pytest.raises(Forbidden), {}, False),
        ('Test 403 when STAFF in disabled_roles.', pytest.raises(Forbidden), {'disabled_roles': {'STAFF'}}, False),
        ('Test OK when STAFF not in disabled_roles.', does_not_raise(), {'disabled_roles': {None}}, False),
        ('Test OK when STAFF in one_of_roles.', does_not_raise(), {'one_of_roles': {'STAFF'}}, False),
        ('Test OK when STAFF IS equals_role.', does_not_raise(), {'equals_role': 'STAFF'}, False),
        (
            'Test UnboundLocalError when system_required set to true -- auth variable not set.',
            pytest.raises(UnboundLocalError),
            {'equals_role': 'STAFF', 'system_required': True},
            False
        ),
        (
            'Test 403 when system_required set to true and correct OrgId provided, but not correct membership type.',
            pytest.raises(Forbidden),
            {'equals_role': 'STAFF', 'system_required': True},
            True
        ),
        (
            'Test OK when system_required set to true, it is STAFF and correct OrgId and membership provided.',
            does_not_raise(),
            {'equals_role': 'ADMIN', 'system_required': True},
            True
        ),
    ])
def test_check_auth_staff_path(session, monkeypatch, test_desc, test_expect, additional_kwargs, add_org_id):
    """Assert and document scenarios for check_auth when STAFF path is concerned."""
    jwt_claims = TestJwtClaims.staff_role

    if add_org_id:
        user = factory_user_model(TestUserInfo.user_test)
        jwt_claims['sub'] = str(user.keycloak_guid)
        jwt_claims['idp_userid'] = user.idp_userid
        org = factory_org_model()
        factory_membership_model(user.id, org.id)
        additional_kwargs['org_id'] = org.id

    patch_token_info(jwt_claims, monkeypatch)
    with test_expect:
        check_auth(**additional_kwargs)


@pytest.mark.parametrize(
    'test_desc,test_expect,additional_kwargs,is_org_member,is_entity_affiliated,product_code_in_jwt',
    [
        (
            'Test 403 when no role checks provided in kwargs, and no org_id or business_identifier.',
            pytest.raises(Forbidden), {}, False, False, ProductCode.BUSINESS.value
        ),
        (
            'Test OK when no role checks provided in kwargs, but has ALL product in jwt. (bypass all checks).',
            does_not_raise(), {}, False, False, 'ALL'
        ),
        (
            'Test OK when business identifier for affiliated entity and member of org.',
            does_not_raise(), {}, True, True, ProductCode.BUSINESS.value
        ),
        (
            'Test OK when business identifier for affiliated entity provided.',
            does_not_raise(), {}, False, True, ProductCode.BUSINESS.value
        ),
        (
            'Test OK when member of the org.',
            does_not_raise(), {}, True, False, ProductCode.BUSINESS.value
        ),
        (
            'Test OK when business identifier provided, not affiliated...',
            does_not_raise(), {'business_identifier': 'SOME_NOT_AFFILIATED'}, False, False, ProductCode.BUSINESS.value
        ),
        (
            'Test OK when org_id provided, not member...',
            does_not_raise(), {'org_id': 123}, False, False, ProductCode.BUSINESS.value
        ),
        (
            'Test OK when org_id provided, not member, and not affiliated business_identifier...',
            does_not_raise(), {'org_id': 123, 'business_identifier': 'SOME_NOT_AFFILIATED'},
            False, False, ProductCode.BUSINESS.value
        ),
    ]
)
def test_check_auth_system_path(session, monkeypatch, test_desc, test_expect, additional_kwargs,
                                is_org_member, is_entity_affiliated, product_code_in_jwt):
    """Assert and document scenarios for check_auth when calls are made by SYSTEM ROLE."""
    jwt_claims = TestJwtClaims.system_role
    user = factory_user_model()
    jwt_claims['sub'] = str(user.keycloak_guid)
    org1 = factory_org_model(org_info=TestOrgInfo.org1)
    org3 = factory_org_model(org_info=TestOrgInfo.org4)
    entity1 = factory_entity_model(entity_info=TestEntityInfo.entity1)
    entity2 = factory_entity_model(entity_info=TestEntityInfo.entity2)
    factory_affiliation_model(entity2.id, org3.id)

    if is_org_member and is_entity_affiliated:
        factory_membership_model(user.id, org1.id)
        factory_product_model(org1.id, product_code=ProductCode.BUSINESS.value)
        factory_affiliation_model(entity1.id, org1.id)
        additional_kwargs['org_id'] = org1.id
        additional_kwargs['business_identifier'] = entity1.business_identifier

    elif is_org_member:
        factory_membership_model(user.id, org1.id)
        factory_product_model(org1.id, product_code=ProductCode.BUSINESS.value)
        additional_kwargs['org_id'] = org1.id

    elif is_entity_affiliated:
        factory_membership_model(user.id, org1.id)
        factory_product_model(org1.id, product_code=ProductCode.BUSINESS.value)
        factory_affiliation_model(entity1.id, org1.id)
        additional_kwargs['business_identifier'] = entity1.business_identifier

    jwt_claims['product_code'] = product_code_in_jwt

    patch_token_info(jwt_claims, monkeypatch)
    with test_expect:
        check_auth(**additional_kwargs)


@pytest.mark.parametrize(
    'test_desc,test_expect,additional_kwargs,is_org_member,is_entity_affiliated',
    [
        (
            'Test HTTPException (403) when no role checks provided in kwargs.',
            pytest.raises(HTTPException), {}, False, False
        ),
        (
            'Test 403 when org member, but no role checks provided in kwargs.',
            pytest.raises(Forbidden), {}, True, False
        ),
        (
            'Test 403 when entity affiliated, but no role checks provided in kwargs.',
            pytest.raises(Forbidden), {}, False, True
        ),
        (
            'Test OK when org member ADMIN and checked for ADMIN role.',
            does_not_raise(), {'equals_role': 'ADMIN'}, True, False
        ),
        (
            'Test OK when affiliated entity and checked for ADMIN role.',
            does_not_raise(), {'equals_role': 'ADMIN'}, False, True
        ),
        (
            'Test OK when org member ADMIN and checked for ADMIN role.',
            does_not_raise(), {'one_of_roles': {'ADMIN'}}, True, False
        ),
        (
            'Test OK when affiliated entity and checked for ADMIN role.',
            does_not_raise(), {'one_of_roles': {'ADMIN'}}, False, True
        ),
        (
            'Test OK when org member ADMIN and checked for ADMIN role.',
            does_not_raise(), {'one_of_roles': {'ADMIN'}}, True, False
        ),
        (
            'Test OK when affiliated entity and checked for ADMIN role.',
            does_not_raise(), {'one_of_roles': {'ADMIN'}}, False, True
        ),
        (
            'Test OK when org member ADMIN and checked for ADMIN role.',
            does_not_raise(), {'disabled_roles': {'STAFF'}}, True, False
        ),
        (
            'Test OK when affiliated entity and checked for ADMIN role.',
            does_not_raise(), {'disabled_roles': {'STAFF'}}, False, True
        ),
        (
            'Test 403 when org member ADMIN and checked for STAFF role.',
            pytest.raises(Forbidden), {'one_of_roles': {'STAFF'}}, True, True
        ),
        (
            'Test 403 when affiliated entity and disabled ADMIN role.',
            pytest.raises(Forbidden), {'disabled_roles': {'ADMIN'}}, True, True
        ),
        (
            'Test 403 when affiliated entity and disabled STAFF role.',
            pytest.raises(Forbidden), {'equals_role': {'STAFF'}}, True, True
        ),
    ]
)
def test_check_auth_public_user_path(session, monkeypatch, test_desc, test_expect, additional_kwargs,
                                     is_org_member, is_entity_affiliated):
    """Assert and document scenarios for check_auth when calls are made by PUBLIC USER ROLE."""
    jwt_claims = TestJwtClaims.public_user_role
    user = factory_user_model(user_info=TestUserInfo.user_tester)
    jwt_claims['sub'] = str(user.keycloak_guid)
    org1 = factory_org_model(org_info=TestOrgInfo.org1)
    org3 = factory_org_model(org_info=TestOrgInfo.org4)
    entity1 = factory_entity_model(entity_info=TestEntityInfo.entity1)
    entity2 = factory_entity_model(entity_info=TestEntityInfo.entity2)
    factory_affiliation_model(entity2.id, org3.id)

    if is_org_member and is_entity_affiliated:
        factory_membership_model(user.id, org1.id)
        factory_product_model(org1.id, product_code=ProductCode.BUSINESS.value)
        factory_affiliation_model(entity1.id, org1.id)
        additional_kwargs['org_id'] = org1.id
        additional_kwargs['business_identifier'] = entity1.business_identifier

    elif is_org_member:
        factory_membership_model(user.id, org1.id)
        factory_product_model(org1.id, product_code=ProductCode.BUSINESS.value)
        additional_kwargs['org_id'] = org1.id

    elif is_entity_affiliated:
        factory_membership_model(user.id, org1.id)
        factory_product_model(org1.id, product_code=ProductCode.BUSINESS.value)
        factory_affiliation_model(entity1.id, org1.id)
        additional_kwargs['business_identifier'] = entity1.business_identifier

    patch_token_info(jwt_claims, monkeypatch)
    with test_expect:
        check_auth(**additional_kwargs)


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

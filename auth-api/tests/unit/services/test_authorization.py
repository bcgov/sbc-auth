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
from tests.utilities.factory_utils import (
    TestOrgInfo, TestOrgTypeInfo, factory_affiliation_model, factory_entity_model, factory_membership_model,
    factory_org_model, factory_product_model, factory_user_model)


def test_get_user_authorizations_for_entity(session):  # pylint:disable=unused-argument
    """Assert that user authorizations for entity is working."""
    user = factory_user_model()
    org = factory_org_model()
    membership = factory_membership_model(user.id, org.id)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    authorization = Authorization.get_user_authorizations_for_entity({
        'sub': str(user.keycloak_guid),
        'realm_access': {
            'roles': ['basic']
        }}, entity.business_identifier)
    assert authorization is not None
    assert authorization.get('orgMembership', None) == membership.membership_type_code

    # Test with invalid user
    authorization = Authorization.get_user_authorizations_for_entity({'sub': str(uuid.uuid4()), 'realm_access': {
        'roles': ['basic']
    }}, entity.business_identifier)
    assert authorization is not None
    assert authorization.get('orgMembership', None) is None

    # Test for passcode users with invalid username
    authorization = Authorization.get_user_authorizations_for_entity(
        {'loginSource': 'PASSCODE', 'username': 'INVALID', 'realm_access': {
            'roles': ['basic']
        }},
        entity.business_identifier)

    assert authorization is not None
    assert authorization.get('orgMembership', None) is None

    # Test for staff users
    authorization = Authorization.get_user_authorizations_for_entity(
        {'loginSource': '', 'realm_access': {'roles': ['staff']}},
        entity.business_identifier)

    assert authorization is not None
    assert authorization.get('orgMembership', None) is None


def test_get_user_authorizations_for_entity_service_account(session):
    """Assert that user authorizations for entity is working."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id, product_code=ProductCode.BUSINESS.value, product_role_codes=None)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    # Test for service accounts with correct product code
    authorization = Authorization.get_user_authorizations_for_entity(
        {'loginSource': '', 'realm_access': {'roles': ['system']}, 'product_code': ProductCode.BUSINESS.value},
        entity.business_identifier)
    assert bool(authorization) is True
    assert authorization.get('orgMembership', None) == 'ADMIN'

    # Test for service accounts with wrong product code
    authorization = Authorization.get_user_authorizations_for_entity(
        {'loginSource': '', 'realm_access': {'roles': ['system']}, 'product_code': 'INVALIDCP'},
        entity.business_identifier)
    assert bool(authorization) is False
    assert authorization.get('orgMembership', None) is None

    # Test for service accounts with no product code
    authorization = Authorization.get_user_authorizations_for_entity(
        {'loginSource': '', 'realm_access': {'roles': ['system']}},
        entity.business_identifier)
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


def test_check_auth(session):  # pylint:disable=unused-argument
    """Assert that check_auth is working as expected."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id, product_code=ProductCode.BUSINESS.value, product_role_codes=None)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    # Test if staff admin can access to STAFF only method
    check_auth({'realm_access': {'roles': ['staff', 'create_accounts']}, 'sub': str(user.keycloak_guid)},
               one_of_roles=[STAFF])

    # Test for staff admin role to only STAFF
    check_auth({'realm_access': {'roles': ['staff', 'create_accounts']}, 'sub': str(user.keycloak_guid)},
               equals_role=STAFF)

    # Test for staff role
    check_auth({'realm_access': {'roles': ['staff']}, 'sub': str(user.keycloak_guid),
                'product_code': ProductCode.BUSINESS.value}, one_of_roles=[STAFF])
    # Test for owner role
    check_auth({'realm_access': {'roles': ['public']}, 'sub': str(user.keycloak_guid),
                'product_code': ProductCode.BUSINESS.value}, one_of_roles=[ADMIN],
               business_identifier=entity.business_identifier)
    # Test for owner role with org id
    check_auth({'realm_access': {'roles': ['public']}, 'sub': str(user.keycloak_guid),
                'product_code': ProductCode.BUSINESS.value}, one_of_roles=[ADMIN],
               org_id=org.id)

    # Test for exception, check for auth if resource is available for STAFF users
    with pytest.raises(HTTPException) as excinfo:
        check_auth({'realm_access': {'roles': ['public']}, 'sub': str(user.keycloak_guid)}, one_of_roles=[STAFF],
                   business_identifier=entity.business_identifier)
        assert excinfo.exception.code == 403

    # Test auth where STAFF role is in disabled role list
    with pytest.raises(HTTPException) as excinfo:
        check_auth({'realm_access': {'roles': ['staff']}, 'sub': str(user.keycloak_guid)}, disabled_roles=[STAFF],
                   business_identifier=entity.business_identifier)
        assert excinfo.exception.code == 403

    # Test auth where STAFF role is exact match
    with pytest.raises(HTTPException) as excinfo:
        check_auth({'realm_access': {'roles': ['public']}, 'sub': str(user.keycloak_guid)}, equals_role=USER,
                   business_identifier=entity.business_identifier)
        assert excinfo.exception.code == 403

    # Test auth where STAFF role is exact match
    with pytest.raises(HTTPException) as excinfo:
        check_auth({'realm_access': {'roles': ['public']}, 'sub': str(user.keycloak_guid)}, equals_role=USER,
                   org_id=org.id)
        assert excinfo.exception.code == 403

        # Test auth where STAFF role is exact match
        with pytest.raises(HTTPException) as excinfo:
            check_auth({'realm_access': {'roles': ['staff', 'create_accounts']}, 'sub': str(user.keycloak_guid)},
                       equals_role=USER,
                       org_id=org.id)
            assert excinfo.exception.code == 403


def test_check_auth_for_service_account_valid_with_org_id(session):  # pylint:disable=unused-argument
    """Assert that check_auth is working as expected."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id, product_code=ProductCode.BUSINESS.value, product_role_codes=None)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    # Test for service account with CP corp type
    check_auth({'realm_access': {'roles': ['system']}, 'product_code': ProductCode.BUSINESS.value}, org_id=org.id)


def test_check_auth_for_service_account_valid_with_business_id(session):  # pylint:disable=unused-argument
    """Assert that check_auth is working as expected."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    factory_product_model(org.id, product_code=ProductCode.BUSINESS.value, product_role_codes=None)
    entity = factory_entity_model()
    factory_affiliation_model(entity.id, org.id)

    # Test for service account with CP corp type
    check_auth({'realm_access': {'roles': ['system']}, 'product_code': ProductCode.BUSINESS.value},
               business_identifier=entity.business_identifier)


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


def test_get_account_authorizations_for_product(session):  # pylint:disable=unused-argument
    """Assert that user authorizations for product is working."""
    user = factory_user_model()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)

    authorization = Authorization.get_account_authorizations_for_product(
        str(user.keycloak_guid),
        org.id,
        'PPR')
    assert authorization is not None
    assert len(authorization.get('roles')) == 0

    # Now add some product subscription for the org
    factory_product_model(org.id)
    authorization = Authorization.get_account_authorizations_for_product(
        str(user.keycloak_guid),
        org.id,
        'PPR')
    assert authorization is not None
    assert len(authorization.get('roles')) == 1
    assert authorization.get('roles')[0] == 'search'

    # Create another org and assert that the roles are empty
    org = factory_org_model(org_info=TestOrgInfo.org2, org_type_info=TestOrgTypeInfo.implicit, org_status_info=None,
                            payment_type_info=None)
    factory_membership_model(user.id, org.id)
    authorization = Authorization.get_account_authorizations_for_product(
        str(user.keycloak_guid),
        org.id,
        'PPR')
    assert authorization is not None
    assert len(authorization.get('roles')) == 0

    factory_product_model(org.id, product_role_codes=['search', 'register'])
    authorization = Authorization.get_account_authorizations_for_product(
        str(user.keycloak_guid),
        org.id,
        'PPR')
    assert authorization is not None
    assert len(authorization.get('roles')) == 2
    assert 'search' in authorization.get('roles')
    assert 'register' in authorization.get('roles')

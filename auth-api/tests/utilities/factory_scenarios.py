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
"""Test Utils.

Test Utility for creating test scenarios.
"""
import uuid
from enum import Enum
from auth_api.services.keycloak_user import KeycloakUser
from random import choice
from string import ascii_lowercase, ascii_uppercase

from config import get_named_config

CONFIG = get_named_config('testing')

JWT_HEADER = {
    'alg': CONFIG.JWT_OIDC_TEST_ALGORITHMS,
    'typ': 'JWT',
    'kid': CONFIG.JWT_OIDC_TEST_AUDIENCE
}


class TestJwtClaims(dict, Enum):
    """Test scenarios of jwt claims."""

    no_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302065',
        'firstname': 'Test',
        'lastname': 'User 2',
        'preferred_username': 'testuser2',
        'realm_access': {
            'roles': [
            ]
        }
    }

    invalid = {
        'sub': 'barfoo',
        'firstname': 'Trouble',
        'lastname': 'Maker',
        'preferred_username': 'troublemaker'
    }

    public_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': 'Test',
        'lastname': 'User',
        'preferred_username': 'testuser',
        'realm_access': {
            'roles': [
                'public_user'
            ]
        }
    }

    edit_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': 'Test',
        'lastname': 'User',
        'preferred_username': 'testuser',
        'realm_access': {
            'roles': [
                'edit'
            ]
        }
    }

    edit_role_2 = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302075',
        'firstname': 'Test',
        'lastname': 'User 2',
        'preferred_username': 'testuser2',
        'realm_access': {
            'roles': [
                'edit'
            ]
        }
    }

    view_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': 'Test',
        'lastname': 'User',
        'preferred_username': 'testuser',
        'realm_access': {
            'roles': [
                'view'
            ]
        }
    }

    staff_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': 'Test',
        'lastname': 'User',
        'preferred_username': 'testuser',
        'realm_access': {
            'roles': [
                'staff'
            ]
        }
    }

    staff_admin_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': 'Test',
        'lastname': 'User',
        'preferred_username': 'testuser',
        'realm_access': {
            'roles': [
                'staff', 'staff_admin'
            ]
        }
    }

    system_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': 'Test',
        'lastname': 'User',
        'preferred_username': 'testuser',
        'realm_access': {
            'roles': [
                'system'
            ]
        },
        'corp_type': 'CP'
    }

    passcode = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': 'Test',
        'lastname': 'User',
        'preferred_username': 'CP1234567',
        'username': 'CP1234567',
        'realm_access': {
            'roles': [
                'system'
            ]
        },
        'loginSource': 'PASSCODE'
    }

    updated_test = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': 'Updated_Test',
        'lastname': 'User',
        'username': 'testuser',
        'realm_access': {
            'roles': [
            ]
        }
    }
    user_test = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': '1b20db59-19a0-4727-affe-c6f64309fd04',
        'firstname': 'Test',
        'lastname': 'User',
        'preferred_username': 'CP1234567',
        'username': 'CP1234567',
        'realm_access': {
            'roles': [
                'edit', 'uma_authorization', 'staff'
            ]
        },
        'loginSource': 'PASSCODE'
    }

    tester_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': 'Test',
        'lastname': 'User',
        'preferred_username': 'testuser',
        'realm_access': {
            'roles': [
                'tester'
            ]
        }
    }

    @staticmethod
    def get_test_real_user(sub):
        """Produce a created user."""
        return {
            'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
            'sub': str(sub),
            'firstname': 'Test',
            'lastname': 'User',
            'preferred_username': 'testuser',
            'realm_access': {
                'roles': [
                    'edit'
                ]
            }
        }

    @staticmethod
    def get_test_user(sub, source: str = 'PASSCODE'):
        """Return test user with subject from argument."""
        return {
            'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
            'sub': sub,
            'firstname': 'Test',
            'lastname': 'User',
            'preferred_username': 'CP1234567',
            'username': 'CP1234567',
            'realm_access': {
                'roles': [
                    'edit', 'uma_authorization', 'staff'
                ]
            },
            'roles': ['edit', 'uma_authorization', 'staff'],
            'loginSource': source
        }


class TestOrgTypeInfo(dict, Enum):
    """Test scenarios of org type."""

    test_type = {'code': 'TEST', 'desc': 'Test'}
    implicit = {'code': 'IMPLICIT', 'desc': 'IMPLICIT'}


class TestPaymentTypeInfo(dict, Enum):
    """Test scenarios of payment type."""

    test_type = {'code': 'TEST', 'desc': 'Test'}


class TestAnonymousMembership(dict, Enum):
    """Test scenarios of org status."""

    @staticmethod
    def generate_random_user(membership: str):
        """Return user with keycloak guid."""
        return {'username': ''.join(choice(ascii_uppercase) for i in range(5)), 'password': 'firstuser',
                'membershipType': membership}


class TestOrgStatusInfo(dict, Enum):
    """Test scenarios of org status."""

    test_status = {'code': 'TEST', 'desc': 'Test'}


class TestOrgInfo(dict, Enum):
    """Test scenarios of org."""

    org1 = {'name': 'My Test Org'}
    org2 = {'name': 'My Test Updated Org'}
    org3 = {'name': 'Third Orgs'}
    org4 = {'name': 'fourth Orgs'}
    org5 = {'name': 'fifth Orgs'}
    org_anonymous = {'name': 'My Test Org', 'accessType': 'ANONYMOUS'}
    invalid = {'foo': 'bar'}
    invalid_name_space = {'name': ''}
    invalid_name_spaces = {'name': '    '}
    invalid_name_start_space = {'name': '  helo'}
    invalid_name_end_space = {'name': '  helo   '}


class TestOrgProductsInfo(dict, Enum):
    """Test scenarios of attaching products to org."""

    org_products1 = {'subscriptions': [{'productCode': 'PPR'}]}
    org_products2 = {'subscriptions': [{'productCode': 'PPR', 'productRoles': ['search', 'File']},
                                       {'productCode': 'DIR_SEARCH', 'productRoles': ['search']}]}


class TestEntityInfo(dict, Enum):
    """Test scenarios of entity."""

    entity1 = {'businessIdentifier': 'CP1234567',
               'businessNumber': '791861073BC0001',
               'name': 'Foobar, Inc.',
               'passCode': '',
               'corpTypeCode': 'CP'}
    entity2 = {'businessIdentifier': 'CP1234568',
               'businessNumber': '791861079BC0001',
               'name': 'BarFoo, Inc.',
               'passCode': '', 'corpTypeCode': 'CP'}
    entity_passcode = {'businessIdentifier': 'CP1234568',
                       'businessNumber': '791861079BC0001',
                       'name': 'Foobar, Inc.',
                       'passCode': '111111111', 'corpTypeCode': 'CP'}
    entity_passcode2 = {'businessIdentifier': 'CP1234568',
                        'businessNumber': '791861078BC0001',
                        'name': 'BarFoo, Inc.',
                        'passCode': '222222222', 'corpTypeCode': 'CP'}

    bc_entity_passcode3 = {'businessIdentifier': 'CP123456890',
                           'businessNumber': '791861078BC0002',
                           'name': 'BarFoo, Inc.3',
                           'passCode': '222222222', 'corpTypeCode': 'BC'}

    bc_entity_passcode4 = {'businessIdentifier': 'CP123456891',
                           'businessNumber': '791861078BC0003',
                           'name': 'BarFoo, Inc.4',
                           'passCode': '222222222', 'corpTypeCode': 'BC'}

    invalid = {'foo': 'bar'}

    entity_lear_mock = {'businessIdentifier': 'CP0002103',
                        'businessNumber': '791861078BC0001',
                        'name': 'BarFoo, Inc.',
                        'passCode': '222222222', 'corpTypeCode': 'CP'}

    entity_lear_mock2 = {'businessIdentifier': 'CP0002106',
                         'businessNumber': '791861078BC0002',
                         'name': 'Foobar, Inc.',
                         'passCode': '222222222', 'corpTypeCode': 'CP'}


class TestAffliationInfo(dict, Enum):
    """Test scenarios of affliation."""

    affliation1 = {'businessIdentifier': 'CP1234567'}
    affliation2 = {'businessIdentifier': 'CP1234568'}
    affiliation3 = {'businessIdentifier': 'CP0002103', 'passCode': '222222222'}
    affiliation4 = {'businessIdentifier': 'CP0002106', 'passCode': '222222222'}
    invalid = {'name': 'CP1234567'}


class TestContactInfo(dict, Enum):
    """Test scenarios of contact."""

    contact1 = {
        'email': 'foo@bar.com',
        'phone': '(555) 555-5555',
        'phoneExtension': '123'
    }

    contact2 = {
        'email': 'bar@foo.com',
        'phone': '(555) 555-5555',
        'phoneExtension': '123'
    }

    invalid = {'email': 'bar'}

    # According to front end email validator and email address standard, the email below is valid email.
    email_valid = {'email': "abc!#$%&'*+-/=?^_`{|.123@test-test.com"}


class TestUserInfo(dict, Enum):
    """Test scenarios of user."""

    user1 = {
        'username': 'CP1234567',
        'firstname': 'Test',
        'lastname': 'User',
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': uuid.uuid4()
    }
    user_staff_admin = {
        'username': 'CP1234567',
        'firstname': 'Test',
        'lastname': 'User',
        'roles': '{edit, uma_authorization, staff_admin}',
        'keycloak_guid': uuid.uuid4()
    }
    user2 = {
        'username': 'CP1234568',
        'firstname': 'Test 2',
        'lastname': 'User',
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': uuid.uuid4()
    }
    user3 = {
        'username': 'CP1234569',
        'firstname': 'Test 3',
        'lastname': 'User',
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': uuid.uuid4()
    }
    user_test = {
        'username': 'CP1234567',
        'firstname': 'Test',
        'lastname': 'User',
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': '1b20db59-19a0-4727-affe-c6f64309fd04'
    }
    user_tester = {
        'username': 'CP1234567',
        'firstname': 'Test',
        'lastname': 'User',
        'roles': '{edit, uma_authorization, tester}',
        'keycloak_guid': '1b20db59-19a0-4727-affe-c6f64309fd04'
    }
    user_anonymous_1 = {
        'username': 'testuser12345',
        'password': 'testuser12345',
    }
    user_anonymous_2 = {
        'username': 'testuser12345',
        'password': 'testuser12345',
    }

    @staticmethod
    def get_user_with_kc_guid(kc_guid: str):
        """Return user with keycloak guid."""
        return {
            'username': 'tester',
            'firstname': 'Test',
            'lastname': 'User',
            'roles': '{edit, uma_authorization, staff}',
            'keycloak_guid': kc_guid
        }


class KeycloakScenario:
    """Keycloak scenario."""

    @staticmethod
    def create_user_request():
        """Return create user request."""
        create_user_request = KeycloakUser()
        create_user_request.user_name = ''.join(choice(ascii_lowercase) for i in range(8))
        create_user_request.password = '1111'
        create_user_request.first_name = 'test_first'
        create_user_request.last_name = 'test_last'
        create_user_request.email = 'testuser1@gov.bc.ca'
        create_user_request.attributes = {'corp_type': 'CP', 'source': 'BCSC'}
        create_user_request.enabled = True
        return create_user_request

    @staticmethod
    def create_user_request_2():
        """Return create user request."""
        create_user_request = KeycloakUser()
        create_user_request.user_name = 'testuser2'
        create_user_request.password = '1111'
        create_user_request.first_name = 'test_first'
        create_user_request.last_name = 'test_last'
        create_user_request.email = 'testuser2@gov.bc.ca'
        create_user_request.attributes = {'corp_type': 'CP', 'source': 'BCSC'}
        create_user_request.enabled = True

        return create_user_request

    # Patch token info
    @staticmethod
    def token_info(kc_guid: str):  # pylint: disable=unused-argument; mocks of library methods
        """Return token info for test."""
        return {
            'sub': kc_guid,
            'username': 'public user',
            'realm_access': {
                'roles': [
                ]
            }
        }


class BulkUserTestScenario:
    """Test scenarios of bulk users."""

    @staticmethod
    def get_bulk_user1_for_org(org_id: str):
        """Generate a bulk user input."""
        return {'users': [
            {'username': 'first2user2238', 'password': 'helo', 'membershipType': 'ADMIN'},
            {'username': 'secon2duse2r248', 'password': 'helo', 'membershipType': 'MEMBER'}
        ],
            'orgId': org_id
        }

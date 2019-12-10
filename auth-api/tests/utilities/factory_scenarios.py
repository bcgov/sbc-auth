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
import os
import uuid
from enum import Enum


JWT_HEADER = {
    'alg': os.getenv('JWT_OIDC_ALGORITHMS'),
    'typ': 'JWT',
    'kid': os.getenv('JWT_OIDC_AUDIENCE')
}


class TestJwtClaims(dict, Enum):
    """Test scenarios of jwt claims."""

    no_role = {
        'iss': os.getenv('JWT_OIDC_ISSUER'),
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

    edit_role = {
        'iss': os.getenv('JWT_OIDC_ISSUER'),
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
        'iss': os.getenv('JWT_OIDC_ISSUER'),
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
        'iss': os.getenv('JWT_OIDC_ISSUER'),
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
        'iss': os.getenv('JWT_OIDC_ISSUER'),
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

    system_role = {
        'iss': os.getenv('JWT_OIDC_ISSUER'),
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': 'Test',
        'lastname': 'User',
        'preferred_username': 'testuser',
        'realm_access': {
            'roles': [
                'system'
            ]
        }
    }

    passcode = {
        'iss': os.getenv('JWT_OIDC_ISSUER'),
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
        'iss': os.getenv('JWT_OIDC_ISSUER'),
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
        'iss': os.getenv('JWT_OIDC_ISSUER'),
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

    @staticmethod
    def get_test_user(sub):
        """Return test user with subject from argument."""
        return {
            'iss': os.getenv('JWT_OIDC_ISSUER'),
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
            'loginSource': 'PASSCODE'
        }


class TestOrgTypeInfo(dict, Enum):
    """Test scenarios of org type."""

    test_type = {'code': 'TEST', 'desc': 'Test'}
    implicit = {'code': 'IMPLICIT', 'desc': 'IMPLICIT'}


class TestPaymentTypeInfo(dict, Enum):
    """Test scenarios of payment type."""

    test_type = {'code': 'TEST', 'desc': 'Test'}


class TestOrgStatusInfo(dict, Enum):
    """Test scenarios of org status."""

    test_status = {'code': 'TEST', 'desc': 'Test'}


class TestOrgInfo(dict, Enum):
    """Test scenarios of org."""

    org1 = {'name': 'My Test Org'}
    org2 = {'name': 'My Test Updated Org'}
    org3 = {'name': 'M'}
    invalid = {'foo': 'bar'}
    invalid_name_space = {'name': ''}
    invalid_name_spaces = {'name': '    '}
    invalid_name_start_space = {'name': '  helo'}
    invalid_name_end_space = {'name': '  helo   '}


class TestEntityInfo(dict, Enum):
    """Test scenarios of entity."""

    entity1 = {'businessIdentifier': 'CP1234567',
               'businessNumber': '791861073BC0001',
               'name': 'Foobar, Inc.',
               'passCode': ''}
    entity2 = {'businessIdentifier': 'CP1234568',
               'businessNumber': '791861079BC0001',
               'name': 'BarFoo, Inc.',
               'passCode': ''}
    entity_passcode = {'businessIdentifier': 'CP1234568',
                       'businessNumber': '791861079BC0001',
                       'name': 'Foobar, Inc.',
                       'passCode': '111111111'}
    entity_passcode2 = {'businessIdentifier': 'CP1234568',
                        'businessNumber': '791861078BC0001',
                        'name': 'BarFoo, Inc.',
                        'passCode': '222222222'}
    invalid = {'foo': 'bar'}
    entity_lear_mock = {'businessIdentifier': 'CP0002103',
                        'businessNumber': '791861078BC0001',
                        'name': 'BarFoo, Inc.',
                        'passCode': '222222222'}
    entity_lear_mock2 = {'businessIdentifier': 'CP0002106',
                         'businessNumber': '791861078BC0002',
                         'name': 'Foobar, Inc.',
                         'passCode': '222222222'}


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
    user2 = {
        'username': 'CP1234568',
        'firstname': 'Test 2',
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

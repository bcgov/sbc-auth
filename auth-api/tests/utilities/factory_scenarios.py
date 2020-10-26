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
from faker import Faker
from random import choice
from string import ascii_lowercase, ascii_uppercase

from auth_api.services.keycloak_user import KeycloakUser
from auth_api.utils.enums import AccessType, IdpHint, LoginSource, ProductCode, OrgType, PaymentMethod
from auth_api.config import get_named_config

fake = Faker()

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
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
            ]
        }
    }

    invalid = {
        'sub': 'barfoo',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
    }

    public_user_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'public_user'
            ]
        }
    }

    public_account_holder_user = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'public_user',
                'account_holder'
            ]
        }
    }

    public_bceid_user = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'public_user',
                'edit'
            ]
        },
        'email': 'test@test.com',
        'loginSource': LoginSource.BCEID.value
    }

    edit_user_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'edit'
            ]
        }
    }

    edit_role_2 = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302075',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'edit'
            ]
        }
    }

    view_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'view'
            ]
        }
    }

    staff_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'staff',
                'edit'
            ]
        }
    }

    staff_view_accounts_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'staff',
                'view_accounts'
            ]
        }
    }

    staff_manage_accounts_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'staff',
                'view_accounts',
                'manage_accounts'
            ]
        }
    }

    staff_admin_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'staff',
                'view_accounts',
                'create_accounts'
            ]
        },
        'roles': [
            'staff', 'edit', 'create_accounts'
        ]
    }

    staff_admin_dir_search_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'staff',
                'create_accounts',
                'view_accounts',
                'edit'
            ]
        },
        'roles': [
            'staff',
            'create_accounts'
        ]
    }

    bcol_admin_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'staff',
                'manage_accounts',
                'view_accounts'
            ]
        },
        'roles': [
            'staff',
            'manage_accounts',
            'view_accounts'
        ]
    }

    system_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'system'
            ]
        },
        'product_code': ProductCode.BUSINESS.value
    }

    passcode = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'username': 'CP1234567',
        'realm_access': {
            'roles': [
                'system'
            ]
        },
        'loginSource': 'PASSCODE',
        'product_code': ProductCode.BUSINESS.value
    }

    updated_test = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
            ]
        }
    }
    user_test = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': '1b20db59-19a0-4727-affe-c6f64309fd04',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
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
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'loginSource': 'BCSC',
        'realm_access': {
            'roles': [
                'tester'
            ]
        }
    }

    anonymous_bcros_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302069',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': f'{IdpHint.BCROS.value}/{fake.user_name()}',
        'accessType': 'ANONYMOUS',
        'loginSource': 'BCROS',
        'realm_access': {
            'roles': [
                'edit'
            ]
        },
        'product_code': 'DIR_SEARCH'
    }

    tester_bceid_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'user_name': fake.user_name(),
        'loginSource': 'BCEID',
        'realm_access': {
            'roles': [
                'tester'
            ]
        }
    }

    @staticmethod
    def get_test_real_user(sub, preferred_username=fake.user_name(), access_ype=''):
        """Produce a created user."""
        return {
            'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
            'sub': str(sub),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'accessType': access_ype,
            'preferred_username': preferred_username,
            'realm_access': {
                'roles': [
                    'edit', 'public_user'
                ]
            }
        }

    @staticmethod
    def get_test_user(sub, source: str = 'PASSCODE'):
        """Return test user with subject from argument."""
        return {
            'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
            'sub': sub,
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'preferred_username': 'CP1234567',
            'username': 'CP1234567',
            'realm_access': {
                'roles': [
                    'edit', 'uma_authorization', 'staff', 'tester'
                ]
            },
            'roles': ['edit', 'uma_authorization', 'staff', 'tester'],
            'loginSource': source
        }


class TestOrgTypeInfo(dict, Enum):
    """Test scenarios of org type."""

    test_type = {'code': 'TEST', 'desc': 'Test'}
    implicit = {'code': 'BASIC', 'desc': 'BASIC'}


class TestPaymentTypeInfo(dict, Enum):
    """Test scenarios of payment type."""

    test_type = {'code': 'TEST', 'desc': 'Test'}


class TestPaymentMethodInfo(dict, Enum):
    """Test scenarios of payment type."""

    @staticmethod
    def get_payment_method_input(payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD):
        """Return payment info payload."""
        return {'paymentInfo': {'paymentMethod': payment_method.value}}


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

    org_onlinebanking = {'name': 'My Test Org', 'paymentInfo': {'paymentMethod': 'ONLINE_BANKING'}}
    org2 = {'name': 'My Test Updated Org'}
    org3 = {'name': 'Third Orgs'}
    org4 = {'name': 'fourth Orgs'}
    org5 = {'name': 'fifth Orgs'}
    org_anonymous = {'name': 'My Test Anon Org', 'accessType': 'ANONYMOUS'}
    org_anonymous_2 = {'name': 'Another test org', 'accessType': 'ANONYMOUS'}
    invalid = {'foo': 'bar'}
    invalid_name_space = {'name': ''}
    invalid_name_spaces = {'name': '    '}
    invalid_name_start_space = {'name': '  helo'}
    invalid_name_end_space = {'name': '  helo   '}
    org_regular_bceid = {
        'name': 'My Test Org',
        'accessType': AccessType.REGULAR_BCEID.value
    }
    org_regular = {
        'name': 'My Test Org',
        'accessType': AccessType.REGULAR.value
    }

    @staticmethod
    def bcol_linked():
        """Return org info for bcol linked info."""
        return {
            'name': 'BC ONLINE TECHNICAL TEAM DEVL',
            'bcOnlineCredential': {
                'userId': 'test',
                'password': 'password'
            },
            'mailingAddress': {
                'street': '1234 Abcd Street',
                'city': 'Test',
                'region': 'BC',
                'postalCode': 'T1T1T1',
                'country': 'CA'
            },
            'typeCode': OrgType.PREMIUM.value
        }

    @staticmethod
    def org_with_mailing_address(name: str = 'BC ONLINE TECHNICAL TEAM DEVL'):
        """Return org info for bcol linked info."""
        return {
            'name': name,
            'mailingAddress': {
                'street': '1234 Abcd Street',
                'city': 'Test',
                'region': 'BC',
                'postalCode': 'T1T1T1',
                'country': 'CA'
            }
        }

    @staticmethod
    def bcol_linked_incomplete_mailing_addrees():
        """Return org info for bcol linked info."""
        return {
            'name': 'BC ONLINE TECHNICAL TEAM DEVL',
            'bcOnlineCredential': {
                'userId': 'test',
                'password': 'password'
            },
            'mailingAddress': {
                'city': 'Test',
                'region': 'BC',
                'postalCode': 'T1T1T1',
                'country': 'CA'
            }
        }

    @staticmethod
    def bcol_linked_invalid_name():
        """Return org info for bcol linked info with invalid name."""
        return {
            'name': 'Test',
            'bcOnlineCredential': {
                'userId': 'test',
                'password': 'password'
            },
            'mailingAddress': {
                'street': '1234 Abcd Street',
                'city': 'Test',
                'region': 'BC',
                'postalCode': 'T1T1T1',
                'country': 'CA'
            }
        }


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
               'corpTypeCode': 'CP',
               'folioNumber': '1234'}
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

    entity_folio_number = {'businessIdentifier': 'CP1234568',
                           'folioNumber': '12345678'}

    name_request = {
        'businessIdentifier': 'NR 1234567',
        'name': 'ABC Corp Inc.',
        'corpTypeCode': 'NR'
    }

    tenp_business = {
        'businessIdentifier': 'QWERTYUIO',
        'name': 'NR 1234567',
        'corpTypeCode': 'TMP'
    }

    temp_business_incoporated = {
        'businessIdentifier': 'QWERTYUIO',
        'name': 'BC1234567890',
        'corpTypeCode': 'TMP'
    }

    business_incoporated = {
        'businessIdentifier': 'BC1234567890',
        'name': 'My New Incorporated Company',
        'corpTypeCode': 'BC'
    }


class TestAffliationInfo(dict, Enum):
    """Test scenarios of affliation."""

    affliation1 = {'businessIdentifier': 'CP1234567'}
    affliation2 = {'businessIdentifier': 'CP1234568'}
    affiliation3 = {'businessIdentifier': 'CP0002103', 'passCode': '222222222'}
    affiliation4 = {'businessIdentifier': 'CP0002106', 'passCode': '222222222'}
    nr_affiliation = {'businessIdentifier': 'NR 1234567', 'phone': '1112223333'}
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
        'username': fake.user_name(),
        'firstname': fake.first_name(),
        'lastname': 'User',
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': uuid.uuid4()
    }
    user_staff_admin = {
        'username': fake.user_name(),
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, staff_admin}',
        'keycloak_guid': uuid.uuid4()
    }
    user2 = {
        'username': fake.user_name(),
        'firstname': fake.first_name(),
        'lastname': 'User',
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': uuid.uuid4()
    }
    user3 = {
        'username': fake.user_name(),
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': uuid.uuid4()
    }
    user_test = {
        'username': 'CP1234567',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': '1b20db59-19a0-4727-affe-c6f64309fd04'
    }
    user_tester = {
        'username': 'CP1234567',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, tester}',
        'keycloak_guid': '1b20db59-19a0-4727-affe-c6f64309fd04'
    }
    user_anonymous_1 = {
        'username': fake.user_name(),
        'password': 'Password@1234',
    }
    user_bcros = {
        'username': f'{IdpHint.BCROS.value}/{fake.user_name()}',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, staff}'
        # dont add a kc_guid
    }

    user_bcros_active = {
        'username': f'{IdpHint.BCROS.value}/{fake.user_name()}',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': uuid.uuid4(),
        'access_type': 'ANONYMOUS',
    }
    user_bceid_tester = {
        'username': f'{fake.user_name()}@{IdpHint.BCEID.value}',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, tester}',
        'keycloak_guid': uuid.uuid4(),
        'access_type': 'BCEID',
    }

    @staticmethod
    def get_bceid_user_with_kc_guid(kc_guid: str):
        """Return user with keycloak guid."""
        return {
            'username': fake.user_name(),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'roles': '{edit, uma_authorization, staff}',
            'keycloak_guid': kc_guid,
            'access_type': 'BCEID',
            'login_source': LoginSource.BCEID.value
        }

    @staticmethod
    def get_user_with_kc_guid(kc_guid: str):
        """Return user with keycloak guid."""
        return {
            'username': fake.user_name(),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'roles': '{edit, uma_authorization, staff}',
            'keycloak_guid': kc_guid
        }


class KeycloakScenario:
    """Keycloak scenario."""

    @staticmethod
    def create_user_request():
        """Return create user request."""
        create_user_request = KeycloakUser()
        user_name = ''.join(choice(ascii_lowercase) for i in range(5))
        create_user_request.user_name = user_name
        create_user_request.password = 'Test@123'
        create_user_request.first_name = 'test_first'
        create_user_request.last_name = 'test_last'
        create_user_request.email = f'{user_name}@gov.bc.ca'
        create_user_request.attributes = {'corp_type': 'CP', 'source': 'BCSC'}
        create_user_request.enabled = True
        return create_user_request

    @staticmethod
    def create_user_by_user_info(user_info: dict):
        """Return create user request."""
        create_user_request = KeycloakUser()
        create_user_request.user_name = user_info['preferred_username']
        create_user_request.password = 'Test@123'
        create_user_request.first_name = user_info['firstname']
        create_user_request.last_name = user_info['lastname']
        create_user_request.attributes = {'source': user_info['loginSource']}
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
            {'username': ''.join(choice(ascii_uppercase) for i in range(5)), 'password': 'Test@12345',
             'membershipType': 'COORDINATOR'},
            {'username': ''.join(choice(ascii_uppercase) for i in range(5)), 'password': 'Test@12345',
             'membershipType': 'USER'}
        ],
            'orgId': org_id
        }


class TestBCOLInfo(dict, Enum):
    """Test scenarios of org."""

    bcol1 = {'bcol_account_id': 'BCOL1'}
    bcol2 = {'bcol_account_id': 'BCOL2'}


class TestAffidavit:
    """Test affidavit scenarios."""

    @staticmethod
    def get_test_affidavit_with_contact(doc_id: str = '1234567890987654323456789876543456787654345678.txt'):
        """Return a dict for affidavit."""
        return {
            'issuer': 'ABC Notaries Inc.',
            'documentId': doc_id,
            'contact': {
                'email': 'foo@bar.com',
                'phone': '(555) 555-5555',
                'phoneExtension': '123'
            }
        }

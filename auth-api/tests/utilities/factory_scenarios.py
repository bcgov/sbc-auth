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
from random import choice
from string import ascii_lowercase, ascii_uppercase

from faker import Faker

from auth_api.config import get_named_config
from auth_api.services.keycloak_user import KeycloakUser
from auth_api.utils.enums import AccessType, AffidavitStatus, IdpHint, LoginSource, OrgType, PaymentMethod, ProductCode

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
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302065',
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
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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

    gov_account_holder_user = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'public_user',
                'account_holder',
                'gov_account_user'
            ]
        },
        'loginSource': LoginSource.IDIR.value
    }

    public_bceid_user = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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

    public_bceid_account_holder_user = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'public_user',
                'edit',
                'account_holder'
            ]
        },
        'email': 'test@test.com',
        'loginSource': LoginSource.BCEID.value
    }

    edit_user_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302075',
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
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'staff',
                'edit'
            ]
        },
        'loginSource': LoginSource.STAFF.value
    }

    staff_manage_business = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'staff',
                'edit',
                'manage_business'
            ]
        },
        'loginSource': LoginSource.STAFF.value
    }

    staff_view_accounts_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'staff',
                'view_accounts'
            ]
        },
        'loginSource': LoginSource.STAFF.value
    }

    staff_manage_accounts_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'staff',
                'view_accounts',
                'manage_accounts'
            ]
        },
        'loginSource': LoginSource.STAFF.value
    }

    staff_admin_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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
        ],
        'loginSource': LoginSource.STAFF.value
    }

    manage_eft_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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
            'staff', 'edit', 'create_accounts', 'manage_eft'
        ],
        'loginSource': LoginSource.STAFF.value
    }

    staff_admin_dir_search_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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
        ],
        'loginSource': LoginSource.STAFF.value
    }

    bcol_admin_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'staff',
                'manage_accounts',
                'view_accounts',
                'suspend_accounts'
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
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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

    system_admin_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'realm_access': {
            'roles': [
                'system',
                'staff',
                'create_accounts'
            ]
        },
        'product_code': 'ALL'
    }

    passcode = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': fake.user_name(),
        'username': 'CP1234567',
        'realm_access': {
            'roles': [
                'system'
            ]
        },
        'roles': [
            'staff',
            'system'
        ],
        'loginSource': 'PASSCODE',
        'product_code': ProductCode.BUSINESS.value
    }

    updated_test = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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
        'idp_userid': '1b20db59-19a0-4727-affe-c6f64309fd04',
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
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302069',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'preferred_username': f'{IdpHint.BCROS.value}/{fake.user_name()}',
        'accessType': 'ANONYMOUS',
        'loginSource': 'BCROS',
        'realm_access': {
            'roles': [
                'edit',
                'anonymous_user',
                'public_user'
            ]
        },
        'product_code': 'DIR_SEARCH'
    }

    tester_bceid_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
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
    def get_test_real_user(sub, preferred_username=fake.user_name(), access_ype='', roles=[], idp_userid=None):
        """Produce a created user."""
        return {
            'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
            'sub': str(sub),
            'idp_userid': idp_userid or str(sub),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'accessType': access_ype,
            'preferred_username': preferred_username,
            'realm_access': {
                'roles': [
                    'edit', 'public_user', *roles
                ]
            },
            'roles': [
                'edit', 'public_user', *roles
            ]
        }

    @staticmethod
    def get_test_user(sub, source: str = 'PASSCODE', roles=['edit', 'staff', 'tester'], idp_userid=None):
        """Return test user with subject from argument."""
        return {
            'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
            'sub': sub,
            'idp_userid': idp_userid or str(sub),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'preferred_username': 'CP1234567',
            'username': 'CP1234567',
            'realm_access': {
                'roles': roles
            },
            'roles': roles,
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

    @staticmethod
    def get_payment_method_input_with_revenue(payment_method: PaymentMethod = PaymentMethod.EJV):
        """Return payment info payload."""
        revenue_account_details = {
            'client': '100',
            'projectCode': 1111111,
            'responsibilityCentre': '22222',
            'serviceLine': '1111111',
            'stob': '9000'
        }
        return {'paymentInfo': {'paymentMethod': payment_method.value, 'revenueAccount': revenue_account_details}}


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

    affiliation_from_org = {'name': 'Test Affiliation Invitation From Org'}
    affiliation_to_org = {'name': 'Test Affiliation Invitation To Org'}
    org1 = {'name': 'My Test Org'}
    org_details = {'name': 'My test Org details'}
    org_branch_name = {'name': 'Foo', 'branchName': 'Bar', }

    org_onlinebanking = {'name': 'My Test Org', 'paymentInfo': {'paymentMethod': 'ONLINE_BANKING'}}
    org2 = {'name': 'My Test Updated Org'}
    org3 = {'name': 'Third Orgs'}
    org4 = {'name': 'fourth Orgs'}
    org5 = {'name': 'fifth Orgs'}
    org_anonymous = {'name': 'My Test Anon Org', 'accessType': 'ANONYMOUS'}
    org_govm = {'name': 'My Test Anon Org', 'branchName': 'Bar', 'accessType': AccessType.GOVM.value}
    org_anonymous_2 = {'name': 'Another test org', 'accessType': 'ANONYMOUS'}
    org_premium = {'name': 'Another test org', 'typeCode': OrgType.PREMIUM.value}
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

    update_org_with_business_type = {
        'businessType': 'LAW',
        'businessSize': '2-5',
        'isBusinessAccount': True
    }

    org_with_products = {
        'name': 'My Test Org',
        'paymentInfo': {
            'paymentMethod': 'ONLINE_BANKING'
        },
        'productSubscriptions': [{'productCode': 'BUSINESS'}, {'productCode': 'VS'}]
    }

    org_with_all_info = {
        'name': 'My Test Org',
        'accessType': AccessType.REGULAR.value,
        'paymentInfo': {
            'paymentMethod': 'ONLINE_BANKING'
        },
        'productSubscriptions': [{'productCode': 'BUSINESS'}, {'productCode': 'VS'}],
        'businessType': 'LAW',
        'businessSize': '2-5',
        'isBusinessAccount': True
    }

    update_org_with_all_info = {
        'accessType': AccessType.REGULAR.value,
        'paymentInfo': {
            'paymentMethod': 'ONLINE_BANKING'
        },
        'productSubscriptions': [{'productCode': 'BUSINESS'}, {'productCode': 'VS'}],
        'businessType': 'LAW',
        'businessSize': '2-5',
        'isBusinessAccount': True
    }

    bceid_org_with_all_info = {
        'name': 'My Test Org',
        'accessType': AccessType.REGULAR_BCEID.value,
        'paymentInfo': {
            'paymentMethod': 'ONLINE_BANKING'
        },
        'productSubscriptions': [{'productCode': 'BUSINESS'}, {'productCode': 'VS'}],
        'businessType': 'LAW',
        'businessSize': '2-5',
        'isBusinessAccount': True
    }

    staff_org = {'name': 'My Test Org', 'typeCode': OrgType.STAFF.value}

    sbc_staff_org = {'name': 'My Test Org', 'typeCode': OrgType.SBC_STAFF.value}

    @staticmethod
    def bcol_linked():
        """Return org info for bcol linked info."""
        return {
            'name': 'BC ONLINE TECHNICAL TEAM DEVL',
            'bcOnlineCredential': {
                'userId': 'test',
                'password': 'password'
            },
            'mailingAddress': TestOrgInfo.get_mailing_address(),
            'typeCode': OrgType.PREMIUM.value
        }

    @staticmethod
    def update_bcol_linked():
        """Return org info for bcol linked info."""
        return {
            'bcOnlineCredential': {
                'userId': 'test',
                'password': 'password'
            },
            'mailingAddress': TestOrgInfo.get_mailing_address(),
            'typeCode': OrgType.PREMIUM.value
        }

    @staticmethod
    def get_mailing_address():
        """Return mailing Address."""
        return {
            'street': '1234 Abcd Street',
            'city': 'Test',
            'region': 'BC',
            'postalCode': 'T1T1T1',
            'country': 'CA'
        }

    @staticmethod
    def org_with_mailing_address(name: str = 'BC ONLINE TECHNICAL TEAM DEVL'):
        """Return org info for bcol linked info."""
        return {
            'name': name,
            'mailingAddress': TestOrgInfo.get_mailing_address()
        }

    @staticmethod
    def update_org_with_mailing_address():
        """Return org info for update org - bcol linked info."""
        return {
            'mailingAddress': TestOrgInfo.get_mailing_address()
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
            'mailingAddress': TestOrgInfo.get_mailing_address().pop('street')
        }

    @staticmethod
    def bcol_linked_different_name():
        """Return org info for bcol linked info with different org name than bcol account name."""
        return {
            'name': 'Test',
            'bcOnlineCredential': {
                'userId': 'test',
                'password': 'password'
            },
            'mailingAddress': TestOrgInfo.get_mailing_address(),
            'typeCode': OrgType.PREMIUM.value
        }


class TestOrgProductsInfo(dict, Enum):
    """Test scenarios of attaching products to org."""

    org_products1 = {'subscriptions': [{'productCode': 'PPR'}]}
    org_products2 = {'subscriptions': [{'productCode': 'VS'},
                                       {'productCode': 'PPR'}]}
    org_products_vs = {'subscriptions': [{'productCode': 'VS'}]}
    org_products_business = {'subscriptions': [{'productCode': 'BUSINESS'}]}
    org_products_nds = {'subscriptions': [{'productCode': 'NDS'}]}
    mhr = {'subscriptions': [{'productCode': 'MHR'}]}
    mhr_qs_lawyer_and_notaries = {'subscriptions': [{'productCode': 'MHR_QSLN', 'externalSourceId': 'ABC101'}]}
    mhr_qs_home_manufacturers = {'subscriptions': [{'productCode': 'MHR_QSHM', 'externalSourceId': 'ABC102'}]}
    mhr_qs_home_dealers = {'subscriptions': [{'productCode': 'MHR_QSHD', 'externalSourceId': 'ABC103'}]}


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
    entity_reset_passcode = {'businessIdentifier': 'CP1234567',
                             'resetPasscode': True,
                             'passcodeResetEmail': 'abc@test.com'}

    invalid = {'foo': 'bar'}

    entity_lear_mock = {'businessIdentifier': 'CP0002103',
                        'businessNumber': '791861078BC0001',
                        'name': 'BarFoo, Inc.',
                        'passCode': '222222222', 'corpTypeCode': 'CP'}

    entity_lear_mock2 = {'businessIdentifier': 'CP0002106',
                         'businessNumber': '791861078BC0002',
                         'name': 'Foobar, Inc.',
                         'passCode': '222222222', 'corpTypeCode': 'CP'}

    entity_lear_mock3 = {'businessIdentifier': 'FM1000001',
                         'businessNumber': '791861078BC0002',
                         'name': 'Foobar, Inc.',
                         'passCode': 'Horton, Connor', 'corpTypeCode': 'SP'}

    entity_folio_number = {'businessIdentifier': 'CP1234568',
                           'folioNumber': '12345678'}

    name_request = {
        'businessIdentifier': 'NR 1234567',
        'name': 'ABC Corp Inc.',
        'corpTypeCode': 'NR'
    }

    temp_business = {
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
    """Test scenarios of affiliation."""

    affiliation1 = {'businessIdentifier': 'CP1234567'}
    affiliation2 = {'businessIdentifier': 'CP1234568'}
    affiliation3 = {'businessIdentifier': 'CP0002103', 'passCode': '222222222'}
    affiliation4 = {'businessIdentifier': 'CP0002106', 'passCode': '222222222'}
    nr_affiliation = {'businessIdentifier': 'NR 1234567', 'phone': '1112223333'}
    new_business_affiliation = {'businessIdentifier': 'CP1234568',
                                'certifiedByName': 'John Wick', 'phone': '1112223333', 'email': 'test@test.com'}
    invalid = {'name': 'CP1234567'}


class DeleteAffiliationPayload(dict, Enum):
    """Test scenarios of delete affiliation."""

    delete_affiliation1 = {'passcodeResetEmail': 'test@gmail.com', 'resetPasscode': True}
    delete_affiliation2 = {'resetPasscode': False}


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
        'keycloak_guid': uuid.uuid4(),
        'idp_userid': uuid.uuid4()
    }
    user_staff_admin = {
        'username': fake.user_name(),
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, staff_admin}',
        'keycloak_guid': uuid.uuid4(),
        'idp_userid': uuid.uuid4(),
        'type': 'STAFF'

    }
    user2 = {
        'username': fake.user_name(),
        'firstname': fake.first_name(),
        'lastname': 'User',
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': uuid.uuid4(),
        'idp_userid': uuid.uuid4()
    }
    user3 = {
        'username': fake.user_name(),
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': uuid.uuid4(),
        'idp_userid': uuid.uuid4()
    }
    user_test = {
        'username': 'CP1234567',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, staff}',
        'keycloak_guid': '1b20db59-19a0-4727-affe-c6f64309fd04',
        'idp_userid': '1b20db59-19a0-4727-affe-c6f64309fd04'
    }
    user_tester = {
        'username': 'CP1234567',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, tester}',
        'keycloak_guid': '1b20db59-19a0-4727-affe-c6f64309fd04',
        'idp_userid': '1b20db59-19a0-4727-affe-c6f64309fd04'
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
        'idp_userid': uuid.uuid4(),
        'access_type': 'ANONYMOUS',
    }
    user_bceid_tester = {
        'username': f'{fake.user_name()}@{IdpHint.BCEID.value}',
        'firstname': fake.first_name(),
        'lastname': fake.last_name(),
        'roles': '{edit, uma_authorization, tester}',
        'keycloak_guid': uuid.uuid4(),
        'idp_userid': uuid.uuid4(),
        'access_type': 'BCEID',
        'loginSource': LoginSource.BCEID.value
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
            'idp_userid': kc_guid,
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
            'keycloak_guid': kc_guid,
            'idp_userid': kc_guid
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
    def get_test_affidavit_with_contact(doc_id: str = '1234567890987654323456789876543456787654345678.txt',
                                        issuer='ABC Notaries Inc.',
                                        email='foo@bar.com'):
        """Return a dict for affidavit."""
        return {
            'issuer': issuer,
            'documentId': doc_id,
            'contact': {
                'email': email,
                'phone': '(555) 555-5555',
                'phoneExtension': '123'
            }
        }

    @staticmethod
    def get_test_affidavit_with_contact_rejected(doc_id: str = '1234567890987654323456789876543456787654345678.txt',
                                                 issuer='ABC Notaries Inc.',
                                                 email='foo@bar.com'):
        """Return a dict for affidavit."""
        return {
            'issuer': issuer,
            'documentId': doc_id,
            'contact': {
                'email': email,
                'phone': '(555) 555-5555',
                'phoneExtension': '123'
            },
            'status_code': AffidavitStatus.REJECTED.value
        }

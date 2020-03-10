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

Test Utility for creating model factory.
"""
import datetime

from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Contact as ContactModel
from auth_api.models import Documents as DocumentsModel
from auth_api.models import Entity as EntityModel
from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.models import PaymentType as PaymentTypeModel
from auth_api.models.membership import Membership as MembershipModel
from auth_api.models.product_subscription_role import ProductSubscriptionRole as ProductSubscriptionRoleModel
from auth_api.models.product_role_code import ProductRoleCode as ProductRoleCodeModel
from auth_api.models.product_subscription import ProductSubscription as ProductSubscriptionModel
from auth_api.models.user import User as UserModel
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import Entity as EntityService
from auth_api.services import Org as OrgService
from tests.utilities.factory_scenarios import (
    JWT_HEADER, TestContactInfo, TestEntityInfo, TestOrgInfo, TestOrgStatusInfo, TestOrgTypeInfo, TestPaymentTypeInfo,
    TestUserInfo)


def factory_auth_header(jwt, claims):
    """Produce JWT tokens for use in tests."""
    return {'Authorization': 'Bearer ' + jwt.create_jwt(claims=claims, header=JWT_HEADER)}


def factory_entity_model(entity_info: dict = TestEntityInfo.entity1, user_id=None):
    """Produce a templated entity model."""
    entity = EntityModel.create_from_dict(entity_info)
    entity.created_by_id = user_id
    entity.save()
    return entity


def factory_entity_service(entity_info: dict = TestEntityInfo.entity1):
    """Produce a templated entity service."""
    entity_model = factory_entity_model(entity_info)
    entity_service = EntityService(entity_model)
    return entity_service


def factory_user_model(user_info: dict = TestUserInfo.user1):
    """Produce a user model."""
    user = UserModel(username=user_info['username'],
                     firstname=user_info['firstname'],
                     lastname=user_info['lastname'],
                     roles=user_info['roles'],
                     keycloak_guid=user_info['keycloak_guid'])

    user.save()
    return user


def factory_membership_model(user_id, org_id, member_type='OWNER', member_status=1):
    """Produce a Membership model."""
    membership = MembershipModel(user_id=user_id,
                                 org_id=org_id,
                                 membership_type_code=member_type,
                                 membership_type_status=member_status)

    membership.created_by_id = user_id
    membership.save()
    return membership


def factory_org_model(org_info: dict = TestOrgInfo.org1,
                      org_type_info: dict = TestOrgTypeInfo.test_type,
                      org_status_info: dict = TestOrgStatusInfo.test_status,
                      payment_type_info: dict = TestPaymentTypeInfo.test_type,
                      user_id=None):
    """Produce a templated org model."""
    org_type = OrgTypeModel.get_default_type()
    if org_type_info['code'] != TestOrgTypeInfo.implicit['code']:
        org_type = OrgTypeModel(code=org_type_info['code'], desc=org_type_info['desc'])
        org_type.save()

    if org_status_info:
        org_status = OrgStatusModel(code=org_status_info['code'], desc=org_status_info['desc'])
        org_status.save()
    else:
        org_status = OrgStatusModel.get_default_status()

    if payment_type_info:
        preferred_payment = PaymentTypeModel(code=payment_type_info['code'], desc=payment_type_info['desc'])
        preferred_payment.save()
    else:
        preferred_payment = PaymentTypeModel.get_default_payment_type()

    org = OrgModel(name=org_info['name'])
    org.org_type = org_type
    org.org_status = org_status
    org.preferred_payment = preferred_payment
    org.created_by_id = user_id
    org.save()

    return org


def factory_org_service(org_info: dict = TestOrgInfo.org1,
                        org_type_info: dict = TestOrgTypeInfo.test_type,
                        org_status_info: dict = TestOrgStatusInfo.test_status,
                        payment_type_info: dict = TestPaymentTypeInfo.test_type):
    """Produce a templated org service."""
    org_model = factory_org_model(org_info=org_info,
                                  org_type_info=org_type_info,
                                  org_status_info=org_status_info,
                                  payment_type_info=payment_type_info)
    org_service = OrgService(org_model)
    return org_service


def factory_affiliation_model(entity_id, org_id):
    """Produce a templated affiliation model."""
    affiliation = AffiliationModel(entity_id=entity_id, org_id=org_id)
    affiliation.save()
    return affiliation


def factory_affiliation_service(entity_id, org_id):
    """Produce a templated affiliation service."""
    affiliation = AffiliationModel(entity=entity_id, org=org_id)
    affiliation.save()
    affiliation_service = AffiliationService(affiliation)
    return affiliation_service


def factory_contact_model(contact_info: dict = TestContactInfo.contact1):
    """Return a valid contact object with the provided fields."""
    contact = ContactModel(email=contact_info['email'])
    contact.save()
    return contact


def factory_invitation(org_id,
                       email='abc123@email.com',
                       sent_date=datetime.datetime.now().strftime('Y-%m-%d %H:%M:%S'),
                       membership_type='MEMBER'):
    """Produce an invite for the given org and email."""
    return {
        'recipientEmail': email,
        'sentDate': sent_date,
        'membership': [
            {
                'membershipType': membership_type,
                'orgId': org_id
            }
        ]
    }


def factory_document_model(version_id, doc_type, content):
    """Produce a Document model."""
    document = DocumentsModel(version_id=version_id,
                              type=doc_type,
                              content=content)

    document.save()
    return document


def factory_product_model(org_id: str,
                          product_code: str = 'PPR',
                          product_role_codes: list = ['search']
                          ):
    """Produce a templated product model."""
    subscription = ProductSubscriptionModel(org_id=org_id, product_code=product_code)
    subscription.save()

    # Save product roles
    for role_code in product_role_codes:
        product_role_code = ProductRoleCodeModel.find_by_code_and_product_code(role_code, product_code)
        product_role = ProductSubscriptionRoleModel(product_subscription_id=subscription.id,
                                                    product_role_id=product_role_code.id)
        product_role.save()

    return subscription

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

from requests.exceptions import HTTPError

from auth_api.models import ActivityLog as ActivityLogModel
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Documents as DocumentsModel
from auth_api.models import Entity as EntityModel
from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.models import Task as TaskModel
from auth_api.models.membership import Membership as MembershipModel
from auth_api.models.product_subscription import ProductSubscription as ProductSubscriptionModel
from auth_api.models.user import User as UserModel
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import Entity as EntityService
from auth_api.services import Org as OrgService
from auth_api.services import Task as TaskService
from auth_api.utils.enums import (
    AccessType, InvitationType, ProductSubscriptionStatus, TaskRelationshipStatus, TaskRelationshipType, TaskStatus,
    TaskTypePrefix)
from auth_api.utils.roles import Role
from tests.utilities.factory_scenarios import (
    JWT_HEADER, TestBCOLInfo, TestContactInfo, TestEntityInfo, TestOrgInfo, TestOrgTypeInfo, TestUserInfo)


def factory_auth_header(jwt, claims):
    """Produce JWT tokens for use in tests."""
    return {'Authorization': 'Bearer ' + jwt.create_jwt(claims=claims, header=JWT_HEADER)}


def factory_entity_model(entity_info: dict = TestEntityInfo.entity1, user_id=None) -> EntityModel:
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
    roles = user_info.get('roles', None)
    if user_info.get('access_type', None) == AccessType.ANONYMOUS.value:
        user_type = Role.ANONYMOUS_USER.name
    elif Role.STAFF.value in roles:
        user_type = Role.STAFF.name
    else:
        user_type = None

    user = UserModel(username=user_info['username'],
                     firstname=user_info['firstname'],
                     lastname=user_info['lastname'],
                     keycloak_guid=user_info.get('keycloak_guid', None),
                     type=user_type,
                     email='test@test.com',
                     login_source=user_info.get('login_source', None),
                     idp_userid=user_info.get('idp_userid', None)
                     )

    user.save()
    return user


def factory_user_model_with_contact(user_info: dict = TestUserInfo.user1, keycloak_guid=None):
    """Produce a user model."""
    user_type = Role.ANONYMOUS_USER.name if user_info.get('access_type', None) == AccessType.ANONYMOUS.value else None
    user = UserModel(username=user_info.get('username', user_info.get('preferred_username')),
                     firstname=user_info['firstname'],
                     lastname=user_info['lastname'],
                     keycloak_guid=user_info.get('keycloak_guid', keycloak_guid),
                     type=user_type,
                     email='test@test.com',
                     login_source=user_info.get('loginSource'),
                     idp_userid=user_info.get('idp_userid', None)
                     )

    user.save()

    contact = factory_contact_model()
    contact.save()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user
    contact_link.save()

    return user


def factory_membership_model(user_id, org_id, member_type='ADMIN', member_status=1):
    """Produce a Membership model."""
    membership = MembershipModel(user_id=user_id,
                                 org_id=org_id,
                                 membership_type_code=member_type,
                                 membership_type_status=member_status)

    membership.created_by_id = user_id
    membership.save()
    return membership


def factory_org_model(org_info: dict = TestOrgInfo.org1,
                      org_type_info: dict = None,
                      org_status_info: dict = None,
                      user_id=None,
                      bcol_info: dict = TestBCOLInfo.bcol1):
    """Produce a templated org model."""
    org_type = OrgTypeModel.get_default_type()
    if org_type_info and org_type_info['code'] != TestOrgTypeInfo.implicit['code']:
        org_type = OrgTypeModel(code=org_type_info['code'], description=org_type_info['desc'])
        org_type.save()

    if org_status_info is not None:
        org_status = OrgStatusModel(code=org_status_info['code'], description=org_status_info['desc'])
        org_status.save()
    else:
        org_status = OrgStatusModel.get_default_status()

    org = OrgModel(name=org_info['name'])
    org.org_type = org_type
    org.access_type = org_info.get('accessType', '')
    org.org_status = org_status
    org.created_by_id = user_id
    org.bcol_account_id = bcol_info.get('bcol_account_id', '')
    org.bcol_user_id = bcol_info.get('bcol_user_id', '')
    org.save()

    return org


def factory_org_service(org_info: dict = TestOrgInfo.org1,
                        org_type_info: dict = None,
                        org_status_info: dict = None,
                        bcol_info: dict = TestBCOLInfo.bcol1):
    """Produce a templated org service."""
    org_model = factory_org_model(org_info=org_info,
                                  org_type_info=org_type_info,
                                  org_status_info=org_status_info,
                                  bcol_info=bcol_info)
    org_service = OrgService(org_model)
    return org_service


def factory_affiliation_model(entity_id, org_id) -> AffiliationModel:
    """Produce a templated affiliation model."""
    affiliation = AffiliationModel(entity_id=entity_id, org_id=org_id)
    affiliation.save()
    return affiliation


def factory_affiliation_model_by_identifier(business_identifier, org_id) -> AffiliationModel:
    """Produce a templated affiliation model."""
    entity = EntityModel.find_by_business_identifier(business_identifier)
    affiliation = AffiliationModel(entity_id=entity.id, org_id=org_id)
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
                       membership_type='USER'):
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


def factory_invitation_anonymous(org_id,
                                 email='abc123@email.com',
                                 sent_date=datetime.datetime.now().strftime('Y-%m-%d %H:%M:%S'),
                                 membership_type='ADMIN'):
    """Produce an invite for the given org and email."""
    return {
        'recipientEmail': email,
        'sentDate': sent_date,
        'type': InvitationType.DIRECTOR_SEARCH.value,
        'membership': [
            {
                'membershipType': membership_type,
                'orgId': org_id
            }
        ]
    }


def factory_document_model(version_id, doc_type, content, content_type='text/html'):
    """Produce a Document model."""
    document = DocumentsModel(version_id=version_id,
                              type=doc_type,
                              content=content,
                              content_type=content_type)

    document.save()
    return document


def factory_product_model(org_id: str,
                          product_code: str = 'PPR'):
    """Produce a templated product model."""
    subscription = ProductSubscriptionModel(org_id=org_id, product_code=product_code,
                                            status_code=ProductSubscriptionStatus.ACTIVE.value)
    subscription.save()

    return subscription


def factory_task_service(user_id: int = 1, org_id: int = 1):
    """Produce a templated task service."""
    task_model = factory_task_model(user_id, org_id, modified_by_id=user_id)
    service = TaskService(task_model)
    return service


def factory_task_model(user_id: int = 1, org_id: int = 1,
                       modified_by_id: int = None, date_submitted: datetime = datetime.datetime.now()):
    """Produce a Task model."""
    task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
    task = TaskModel(id=user_id,
                     name='foo',
                     date_submitted=date_submitted,
                     relationship_type=TaskRelationshipType.ORG.value,
                     relationship_id=org_id,
                     type=task_type,
                     status=TaskStatus.OPEN.value,
                     related_to=user_id,
                     relationship_status=TaskRelationshipStatus.PENDING_STAFF_REVIEW.value,
                     modified_by_id=modified_by_id
                     )
    task.save()
    return task


def factory_task_models(count: int, user_id: int):
    """Produce a collection of Task models."""
    task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
    for i in range(0, count):
        task = TaskModel(name='TEST {}'.format(i), date_submitted=datetime.datetime.now(),
                         relationship_type=TaskRelationshipType.ORG.value,
                         relationship_id=10, type=task_type,
                         status=TaskStatus.OPEN.value,
                         related_to=user_id,
                         relationship_status=TaskRelationshipStatus.PENDING_STAFF_REVIEW.value)
        task.save()


def factory_activity_log_model(actor: str, action: str, item_type: str = 'Account', item_name='Foo Bar', item_id=10,
                               item_value: str = 'Val',
                               org_id=10,
                               remote_addr=''):
    """Create a Log Model."""
    activity_log = ActivityLogModel(
        actor_id=actor,
        action=action,
        item_name=item_name,
        item_id=item_id,
        item_type=item_type,
        item_value=item_value,
        remote_addr=remote_addr,
        org_id=org_id
    )
    activity_log.save()


def patch_token_info(claims, monkeypatch):
    """Patch token info to mimic g."""

    def token_info():
        """Return token info."""
        return claims

    monkeypatch.setattr('auth_api.utils.user_context._get_token_info', token_info)


def get_tos_latest_version():
    """Return latest tos version."""
    return '5'


def patch_pay_account_post(monkeypatch):
    """Patch pay account post success (200 or 201)."""
    class MockPayResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        @staticmethod
        def json():
            return {}

        def raise_for_status(self):
            pass

    monkeypatch.setattr('auth_api.services.rest_service.RestService.post', lambda *args,
                        **kwargs: MockPayResponse(None, 200))


def patch_pay_account_put(monkeypatch):
    """Patch pay account post success (200 or 201)."""
    class MockPayResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        @staticmethod
        def json():
            return {}

        def raise_for_status(self):
            pass

    monkeypatch.setattr('auth_api.services.rest_service.RestService.put', lambda *args,
                        **kwargs: MockPayResponse(None, 200))


def patch_pay_account_delete(monkeypatch):
    """Patch pay account delete success."""
    class MockPayResponse:

        @staticmethod
        def json():
            return {}

        def raise_for_status(self):
            pass

    monkeypatch.setattr('auth_api.services.rest_service.RestService.delete', lambda *args, **kwargs: MockPayResponse())


def patch_pay_account_delete_error(monkeypatch):
    """Patch pay account delete error."""
    class MockPayResponse:

        @staticmethod
        def json():
            return {'type': 'OUTSTANDING_CREDIT', 'title': 'OUTSTANDING_CREDIT'}

        def raise_for_status(self):
            raise HTTPError('TEST ERROR')

    monkeypatch.setattr('auth_api.services.rest_service.RestService.delete', lambda *args, **kwargs: MockPayResponse())


def patch_get_firms_parties(monkeypatch):
    """Patch pay account delete success."""
    class MockPartiesResponse:

        @staticmethod
        def json():
            return {
                'parties': [
                    {
                        'officer': {
                            'email': 'test@email.com',
                            'firstName': 'Connor',
                            'lastName': 'Horton',
                            'partyType': 'person'
                        },
                        'roles': [
                            {
                                'appointmentDate': '2022-03-01',
                                'cessationDate': 'None',
                                'roleType': 'Partner'
                            }
                        ]
                    }
                ]
            }

        def raise_for_status(self):
            pass

    monkeypatch.setattr('auth_api.services.rest_service.RestService.get', lambda *args, **kwargs: MockPartiesResponse())

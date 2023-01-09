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
"""Test suite for the integrations to NATS Queue."""
import uuid
from auth_api.utils.base_enum import BaseEnum

from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.models.membership import Membership as MembershipModel
from auth_api.models.user import User as UserModel
from auth_api.utils.enums import AccessType


def factory_org_model(org_name: str = 'Test ORg',
                      user_id=None):
    """Produce a templated org model."""
    org_type = OrgTypeModel.get_default_type()
    org_status = OrgStatusModel.get_default_status()
    org = OrgModel(name=org_name)
    org.org_type = org_type
    org.access_type = AccessType.REGULAR.value
    org.org_status = org_status
    org.created_by_id = user_id
    org.save()

    return org


def factory_user_model_with_contact():
    """Produce a user model."""
    user_info = {
        'username': 'foo',
        'firstname': 'bar',
        'lastname': 'User',
        'keycloak_guid': uuid.uuid4()
    }

    user = UserModel(username=user_info['username'],
                     firstname=user_info['firstname'],
                     lastname=user_info['lastname'],
                     keycloak_guid=user_info.get('keycloak_guid', None),
                     type=user_info.get('access_type', None),
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


def factory_contact_model():
    """Return a valid contact object with the provided fields."""
    contact_info = {
        'email': 'foo@bar.com',
        'phone': '(555) 555-5555',
        'phoneExtension': '123'
    }
    contact = ContactModel(email=contact_info['email'])
    contact.save()
    return contact


class TestUserInfo(dict, BaseEnum):
    """Test scenarios of user."""

    user1 = {
        'username': 'foo',
        'firstname': 'bar',
        'lastname': 'User',
        'keycloak_guid': uuid.uuid4()
    }

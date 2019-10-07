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
import uuid

from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Entity as EntityModel
from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.models import PaymentType as PaymentTypeModel
from auth_api.models.membership import Membership
from auth_api.models.user import User


def factory_entity_model():
    """Produce a templated entity model."""
    entity = EntityModel(business_identifier='CP1234567', business_number='791861073BC0001', name='Foobar, Inc.')
    entity.save()
    return entity


def factory_user_model():
    """Produce a user model."""
    user = User(username='CP1234567',
                roles='{edit, uma_authorization, staff}',
                keycloak_guid=uuid.uuid4())

    user.save()
    return user


def factory_membership_model(user_id, org_id, member_type='OWNER'):
    """Produce a Membership model."""
    membership = Membership(user_id=user_id,
                            org_id=org_id,
                            membership_type_code=member_type)

    membership.save()
    return membership


def factory_org_model(name):
    """Produce a templated org model."""
    org_type = OrgTypeModel(code='TEST', desc='Test')
    org_type.save()

    org_status = OrgStatusModel(code='TEST', desc='Test')
    org_status.save()

    preferred_payment = PaymentTypeModel(code='TEST', desc='Test')
    preferred_payment.save()

    org = OrgModel(name=name)
    org.org_type = org_type
    org.org_status = org_status
    org.preferred_payment = preferred_payment
    org.save()

    return org


def factory_affiliation_model(entity_id, org_id):
    """Produce a templated affiliation model."""
    affiliation = AffiliationModel(entity_id=entity_id, org_id=org_id)
    affiliation.save()
    return affiliation

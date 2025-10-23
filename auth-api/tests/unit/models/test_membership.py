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
"""Tests for the Org model.

Test suite to ensure that the Org model routines are working as expected.
"""

from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.models import PaymentType as PaymentTypeModel
from auth_api.utils.roles import ADMIN
from tests.utilities.factory_scenarios import TestUserInfo
from tests.utilities.factory_utils import factory_user_model


def factory_membersip_model(session):
    """Produce a templated org model."""
    user = factory_user_model()
    org_type = OrgTypeModel(code="TEST", description="Test")
    session.add(org_type)
    session.commit()

    org_status = OrgStatusModel(code="TEST", description="Test")
    session.add(org_status)
    session.commit()

    preferred_payment = PaymentTypeModel(code="TEST", description="Test")
    session.add(preferred_payment)
    session.commit()
    org = OrgModel(name="Test Org")
    org.org_type = org_type
    org.org_status = OrgStatusModel.get_default_status()
    org.preferred_payment = preferred_payment
    org.save()

    membership = MembershipModel(org_id=org.id, user_id=user.id, membership_type_code=ADMIN, status=1)
    membership.save()
    return membership


def test_get_count_active_owner_org_id(session):  # pylint:disable=unused-argument
    """Assert that an Org can be updated from a dictionary."""
    membership = factory_membersip_model(session)

    assert MembershipModel.get_count_active_owner_org_id(membership.org_id) == 1


def test_get_count_active_owner_org_id_multiple(session):  # pylint:disable=unused-argument
    """Assert that an Org can be updated from a dictionary."""
    membership1 = factory_membersip_model(session)
    user2 = factory_user_model(TestUserInfo.user2)

    membership2 = MembershipModel(org_id=membership1.org_id, user_id=user2.id, membership_type_code=ADMIN, status=1)
    membership2.save()

    assert MembershipModel.get_count_active_owner_org_id(membership2.org_id) == 2

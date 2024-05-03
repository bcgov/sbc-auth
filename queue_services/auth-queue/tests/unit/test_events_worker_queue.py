# Copyright © 2024 Province of British Columbia
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
"""Test Suite to ensure the worker routines are working as expected."""
from auth_api.models import Org as OrgModel
from auth_api.utils.enums import OrgStatus
from sbc_common_components.utils.enums import QueueMessageTypes

from tests.unit import factory_org_model

from .utils import helper_add_lock_unlock_event_to_queue


def test_lock_and_unlock(app, session, client):
    """Assert that the update internal payment records works."""
    org = factory_org_model()

    helper_add_lock_unlock_event_to_queue(client, QueueMessageTypes.NSF_LOCK_ACCOUNT.value, org_id=org.id)

    new_org = OrgModel.find_by_org_id(org.id)
    assert new_org.status_code == OrgStatus.NSF_SUSPENDED.value

    helper_add_lock_unlock_event_to_queue(client, QueueMessageTypes.NSF_UNLOCK_ACCOUNT.value, org_id=org.id)

    new_org = OrgModel.find_by_org_id(org.id)
    assert new_org.status_code == OrgStatus.ACTIVE.value

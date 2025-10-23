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

from unittest.mock import patch

from auth_api.models import Org as OrgModel
from auth_api.utils.enums import OrgStatus
from sbc_common_components.utils.enums import QueueMessageTypes

from . import factory_org_model
from .utils import helper_add_lock_unlock_event_to_queue


@patch("auth_queue.resources.worker.publish_to_mailer")
def test_lock_and_unlock(mock_publish_to_mailer, app, session, client):  # pylint: disable=unused-argument
    """Assert that the update internal payment records works."""
    org = factory_org_model()

    helper_add_lock_unlock_event_to_queue(client, QueueMessageTypes.NSF_LOCK_ACCOUNT.value, org_id=org.id)

    new_org = OrgModel.find_by_org_id(org.id)
    assert new_org.status_code == OrgStatus.NSF_SUSPENDED.value
    assert mock_publish_to_mailer.call_count == 1
    mock_publish_to_mailer.reset_mock()

    helper_add_lock_unlock_event_to_queue(client, QueueMessageTypes.NSF_UNLOCK_ACCOUNT.value, org_id=org.id)

    new_org = OrgModel.find_by_org_id(org.id)
    assert new_org.status_code == OrgStatus.ACTIVE.value
    assert mock_publish_to_mailer.call_count == 1
    mock_publish_to_mailer.reset_mock()

    helper_add_lock_unlock_event_to_queue(
        client,
        QueueMessageTypes.NSF_LOCK_ACCOUNT.value,
        org_id=org.id,
        skip_notification=True,
    )

    new_org = OrgModel.find_by_org_id(org.id)
    assert new_org.status_code == OrgStatus.NSF_SUSPENDED.value
    assert mock_publish_to_mailer.call_count == 0

    helper_add_lock_unlock_event_to_queue(
        client,
        QueueMessageTypes.NSF_UNLOCK_ACCOUNT.value,
        org_id=org.id,
        skip_notification=True,
    )

    new_org = OrgModel.find_by_org_id(org.id)
    assert new_org.status_code == OrgStatus.ACTIVE.value
    assert mock_publish_to_mailer.call_count == 0

# Copyright © 2025 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""helper to publish to mailer."""
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from flask import current_app
from simple_cloudevent import SimpleCloudEvent
from structured_logging import StructuredLogging

from auth_api.models import Membership as MembershipModel
from auth_api.services.flags import flags
from auth_api.services.gcp_queue import GcpQueue, queue
from auth_api.services.user import User as UserService
from auth_api.utils.enums import QueueSources, Status

logger = StructuredLogging.get_logger()


@dataclass
class AccountEvent:
    """Used account management queue messages."""

    account_id: int
    actioned_by: str
    business_identifier: Optional[str] = None
    user_ids: Optional[List[int]] = None
    user_id: Optional[int] = None


def publish_account_event(
    queue_message_type: str, data: AccountEvent = None, source: str = QueueSources.AUTH_API.value
):
    """Publish to auth event topic."""
    payload = {
        "accountId": data.account_id,
        "businessIdentifier": data.business_identifier,
        "actionedBy": data.actioned_by,
        "actionCategory": "account-management",
    }

    if data.user_ids:
        payload["userIds"] = data.user_ids
    else:
        payload["user_id"] = data.user_id

    cloud_event = SimpleCloudEvent(
        id=str(uuid.uuid4()),
        source=source,
        subject=None,
        time=datetime.now(tz=timezone.utc).isoformat(),
        type=queue_message_type,
        data=payload,
    )
    try:
        queue.publish(current_app.config.get("AUTH_EVENT_TOPIC"), GcpQueue.to_queue_message(cloud_event))
    except Exception as e:  # NOQA # pylint: disable=broad-except
        error_msg = f"Failed to publish to auth event topic {e}"
        logger.error(error_msg)


def publish_affiliation_event(queue_message_type: str, org_id: int, business_identifier: str):
    """Publish affiliation event to topic."""
    if flags.is_on("enable-publish-account-events", default=False) is True:
        current_user: UserService = UserService.find_by_jwt_token(silent_mode=True)
        member_ids = [
            membership.user_id
            for membership in MembershipModel.find_members_by_org_id(org_id)
            if membership.status == Status.ACTIVE.value
        ]
        publish_account_event(
            queue_message_type=queue_message_type,
            data=AccountEvent(
                account_id=org_id,
                business_identifier=business_identifier,
                actioned_by=current_user.identifier if current_user else None,
                user_ids=member_ids,
            ),
        )


def publish_team_member_event(queue_message_type: str, org_id: int, user_id: int):
    """Publish team member removed event to topic."""
    if flags.is_on("enable-publish-account-events", default=False) is True:
        current_user: UserService = UserService.find_by_jwt_token(silent_mode=True)
        publish_account_event(
            queue_message_type=queue_message_type,
            data=AccountEvent(
                account_id=org_id, actioned_by=current_user.identifier if current_user else None, user_id=user_id
            ),
        )

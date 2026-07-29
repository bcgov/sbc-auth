# Copyright © 2026 Province of British Columbia
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
"""Task to do a basic integration permission check without affecting data."""

import uuid
from datetime import UTC, datetime

from flask import current_app
from simple_cloudevent import SimpleCloudEvent
from sqlalchemy import text

from auth_api.models import db
from auth_api.services.gcp_queue import GcpQueue, queue
from auth_api.utils.enums import QueueSources


class AuthJobPermissionCheckTask:  # pylint: disable=too-few-public-methods
    """Validate job permissions."""

    @classmethod
    def check(cls):
        """Attempt operations that require permissions."""
        # test database connectivity/permissions
        db.session.execute(text("SELECT 1"))

        # test account mailer pubsub publish permissions
        cloud_event = SimpleCloudEvent(
            id=str(uuid.uuid4()),
            source=QueueSources.AUTH_JOBS.value,
            subject=None,
            time=datetime.now(tz=UTC).isoformat(),
            type="HELLO",
            data={"hello": "world"},
        )
        queue.publish(current_app.config.get("ACCOUNT_MAILER_TOPIC"), GcpQueue.to_queue_message(cloud_event))

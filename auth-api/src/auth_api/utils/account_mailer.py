# Copyright © 2024 Province of British Columbia
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
from datetime import datetime, timezone
from flask import current_app
from simple_cloudevent import SimpleCloudEvent

from auth_api.services.gcp_queue import GcpQueue, queue


def publish_to_mailer(notification_type, data=None, source='sbc-auth-auth-api'):
    """Publish to Account Mailer."""
    cloud_event = SimpleCloudEvent(
        id=str(uuid.uuid4()),
        source=source,
        subject=None,
        time=datetime.now(tz=timezone.utc).isoformat(),
        type=notification_type,
        data=data
    )
    queue.publish(current_app.config.get('ACCOUNT_MAILER_TOPIC'), GcpQueue.to_queue_message(cloud_event))

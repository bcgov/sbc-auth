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
"""Service for publishing the activity stream data."""
import uuid
from datetime import datetime, timezone

from flask import current_app, g
from sentry_sdk import capture_message
from simple_cloudevent import SimpleCloudEvent
from sqlalchemy_continuum.plugins.flask import fetch_remote_addr

from auth_api.config import get_named_config
from auth_api.models.dataclass import Activity
from auth_api.models import User as UserModel
from auth_api.services.gcp_queue import GcpQueue, queue
from auth_api.utils.enums import QueueMessageTypes


CONFIG = get_named_config()


class ActivityLogPublisher:  # pylint: disable=too-many-instance-attributes, too-few-public-methods
    """Class for Activity Log Publishing."""

    @staticmethod
    def publish_activity(activity: Activity):  # pylint:disable=unused-argument
        """Publish the activity using the given details."""
        try:
            # find user_id if haven't passed in
            if not activity.actor_id and g and 'jwt_oidc_token_info' in g:
                user: UserModel = UserModel.find_by_jwt_token()
                activity.actor_id = user.id if user else None
            data = {
                'actorId': activity.actor_id,
                'action': activity.action,
                'itemType': 'ACCOUNT',
                'itemName': activity.name,
                'itemId': activity.id,
                'itemValue': activity.value,
                'orgId': activity.org_id,
                'remoteAddr': fetch_remote_addr(),
                'createdAt': f'{datetime.now()}'
            }
            cloud_event = SimpleCloudEvent(
                id=str(uuid.uuid4()),
                source='sbc-auth-auth-api',
                subject=None,
                time=datetime.now(tz=timezone.utc).isoformat(),
                type=QueueMessageTypes.ACTIVITY_LOG.value,
                data=data
            )
            queue.publish(CONFIG.ACTIVITY_LISTENER_TOPIC, GcpQueue.to_queue_message(cloud_event))
        except Exception as err:  # noqa: B902 # pylint: disable=broad-except
            capture_message('Activity Queue Publish Event Error:' + str(err), level='error')
            current_app.logger.error('Activity Queue Publish Event Error:', exc_info=True)

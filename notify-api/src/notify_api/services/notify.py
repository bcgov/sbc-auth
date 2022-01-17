# Copyright © 2019 Province of British Columbia
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
"""Service for managing Invitation data."""
import logging

from sqlalchemy.orm import Session

from notify_api.core.settings import get_api_settings
from notify_api.core.queue_publisher import publish
from notify_api.db.crud import content as ContentCRUD
from notify_api.db.crud import notification as NotificaitonCRUD
from notify_api.db.models.notification import NotificationRequest, NotificationUpdate
from notify_api.db.models.notification_status import NotificationStatusEnum


logger = logging.getLogger(__name__)


class NotifyService:  # pylint: disable=too-few-public-methods
    """Class that manages notification."""

    def __init__(self):
        """Return a Notification service instance."""

    @staticmethod
    async def find_notification(db_session: Session, notification_id: int):
        """Get notification by an id."""
        notification = await NotificaitonCRUD.find_notification_by_id(db_session, notification_id=notification_id)
        return notification

    @staticmethod
    async def find_notifications_by_status(db_session: Session, status: str):
        """Get notifications by status."""
        notifications = None
        if status == NotificationStatusEnum.FAILURE:
            seconds = get_api_settings().DELIVERY_FAILURE_RETRY_TIME_FRAME
            notifications = await NotificaitonCRUD.find_notifications_by_status_time(db_session,
                                                                                     status,
                                                                                     seconds)
        else:
            notifications = await NotificaitonCRUD.find_notifications_by_status(db_session, status)

        return notifications

    @staticmethod
    async def send_notification(db_session: Session, notification: NotificationRequest):
        """Create a new notification and send it out."""
        new_notification = await NotificaitonCRUD.create_notification(db_session, notification=notification)

        # push the email to the queue service
        await publish(payload=new_notification.id)

        return new_notification

    @staticmethod
    async def update_notification_status(db_session: Session, notification: NotificationUpdate):
        """Create a new notification and send it out."""
        notification_exists = await NotificaitonCRUD.find_notification_by_id(db_session, notification.id)
        if notification_exists:
            notification_exists.sent_date = notification.sent_date
            notification_exists.status_code = notification.notify_status
            updated_notification = await NotificaitonCRUD.update_notification(db_session, notification_exists)
            if notification_exists.status_code == NotificationStatusEnum.DELIVERED:
                content_exists = await ContentCRUD.find_content_by_notification_id(db_session, notification.id)
                if content_exists:
                    content_exists.body = ''
                    await ContentCRUD.update_content(db_session, content_exists)
            return updated_notification

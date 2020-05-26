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
"""Notification CRUD."""
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from notify_api.db.crud import content as ContentCRUD
from notify_api.db.models.notification import NotificationModel, NotificationRequest, NotificationUpdate
from notify_api.db.models.notification_status import NotificationStatusEnum
from notify_api.db.models.notification_type import NotificationTypeEnum


logger = logging.getLogger(__name__)


async def find_notification_by_id(db_session: Session, notification_id: int):
    """Get notification by id."""
    db_notification = db_session.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
    return db_notification


async def find_notifications_by_status(db_session: Session, status: str):
    """Get notificaitons by status."""
    db_notifications = db_session.query(NotificationModel).filter(NotificationModel.status_code == status).all()
    return db_notifications


async def find_notifications_by_status_time(db_session: Session, status: str, seconds: int):
    """Fet notificaitons by status and specific time frame."""
    timebefore: datetime = datetime.utcnow() - timedelta(seconds=seconds)

    db_notifications = db_session.query(NotificationModel)\
        .filter(NotificationModel.status_code == status)\
        .filter(NotificationModel.request_date > timebefore).all()

    return db_notifications


async def create_notification(db_session: Session, notification: NotificationRequest):
    """Create notification."""
    db_notification = NotificationModel(recipients=notification.recipients,
                                        request_date=datetime.utcnow(),
                                        request_by=notification.request_by,
                                        type_code=NotificationTypeEnum.EMAIL,
                                        status_code=NotificationStatusEnum.PENDING)
    db_session.add(db_notification)
    db_session.commit()
    db_session.refresh(db_notification)

    # save email content
    await ContentCRUD.create_content(db_session,
                                     content=notification.content,
                                     notification_id=db_notification.id)

    return db_notification


async def update_notification(db_session: Session, notification: NotificationUpdate):
    """Update notification."""
    db_notification = notification
    db_session.add(db_notification)
    db_session.commit()
    db_session.refresh(db_notification)
    return db_notification

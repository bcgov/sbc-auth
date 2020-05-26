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
"""API endpoints for managing a notify resource."""
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette.requests import Request

from notify_api.core.authentication import requires
from notify_api.db.database import get_db
from notify_api.db.models.notification import NotificationRequest, NotificationResponse
from notify_api.services.notify import NotifyService


ROUTER = APIRouter()


@ROUTER.get('/{notification_id}', response_model=NotificationResponse)
@requires('authenticated')
async def find_notification(request: Request,  # pylint: disable=unused-argument
                            notification_id: int = Path(...),
                            db_session: Session = Depends(get_db)):
    """Get notification endpoint by id."""
    notification = await NotifyService.find_notification(db_session, notification_id=notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail='Notification not found')
    return notification


@ROUTER.get('/notifications/{status}', response_model=List[NotificationResponse])
@requires('authenticated')
async def find_notifications(request: Request,  # pylint: disable=unused-argument
                             status: str = Path(...),
                             db_session: Session = Depends(get_db)):
    """Get notifications endpoint by status."""
    notifications = await NotifyService.find_notifications_by_status(db_session, status)
    return notifications


@ROUTER.post('/', response_model=NotificationResponse)
@requires('authenticated')
async def send_notification(request: Request,
                            notification: NotificationRequest = Body(...),
                            db_session: Session = Depends(get_db)):
    """Create and send notification endpoint."""
    if request.user.display_name:
        notification.request_by = request.user.display_name

    notification = await NotifyService.send_notification(db_session, notification)
    return notification

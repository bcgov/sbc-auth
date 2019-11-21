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

"""The Unit Test for the Service."""
from datetime import datetime
from unittest.mock import patch
import pytest

from notify_api.core import queue_publisher
from notify_api.db.models.notification import NotificationModel, NotificationRequest, NotificationUpdate
from notify_api.services.notify import NotifyService
from tests.utilities.factory_scenarios import NOTIFICATION_DATA, NOTIFICATION_REQUEST_DATA


def test_find_notification_by_id(session, loop):
    """Assert the test can retrieve notification by id."""
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    result = loop.run_until_complete(
        NotifyService.find_notification(session, notification.id)
    )
    assert result == notification
    assert result.id == NOTIFICATION_DATA[0]['id']
    assert result.recipients == NOTIFICATION_DATA[0]['recipients']


def test_find_notification_by_status(session, loop):
    """Assert the test can retrieve notification by status."""
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    result = loop.run_until_complete(
        NotifyService.find_notifications_by_status(session, notification.status_code)
    )
    assert result[0] == notification
    assert result[0].id == NOTIFICATION_DATA[0]['id']
    assert result[0].recipients == NOTIFICATION_DATA[0]['recipients']


def test_find_notification_by_status_time(session, loop):
    """Assert the test can retrieve notification by status and time frame."""
    notification = NotificationModel(**NOTIFICATION_DATA[2])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    result = loop.run_until_complete(
        NotifyService.find_notifications_by_status(session, notification.status_code)
    )
    assert result[0] == notification
    assert result[0].id == NOTIFICATION_DATA[2]['id']
    assert result[0].recipients == NOTIFICATION_DATA[2]['recipients']


def test_create_notification(session, loop):
    """Assert the test can create notification."""
    result = loop.run_until_complete(
        NotifyService.send_notification(session, NotificationRequest(**NOTIFICATION_REQUEST_DATA[0]))
    )
    assert result.id == NOTIFICATION_DATA[0]['id']
    assert result.recipients == NOTIFICATION_DATA[0]['recipients']


def test_update_notification(session, loop):
    """Assert the test can update notification."""
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    update_notification: NotificationUpdate = NotificationUpdate(id=notification.id,
                                                                 sent_date=datetime.now(),
                                                                 notify_status='FAILURE')
    result = loop.run_until_complete(
        NotifyService.update_notification_status(session, update_notification)
    )
    assert result == notification
    assert result.id == NOTIFICATION_DATA[0]['id']
    assert result.recipients == NOTIFICATION_DATA[0]['recipients']
    assert result.status_code == 'FAILURE'


def test_update_notification_no_exists(session, loop):
    update_notification: NotificationUpdate = NotificationUpdate(id=999,
                                                                 sent_date=datetime.now(),
                                                                 notify_status='FAILURE')
    result = loop.run_until_complete(
        NotifyService.update_notification_status(session, update_notification)
    )
    assert result is None
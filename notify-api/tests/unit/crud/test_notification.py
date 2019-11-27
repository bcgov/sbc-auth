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

"""The Unit Test for the CRUD."""
from datetime import datetime

from notify_api.db.crud import notification as NotificaitonCRUD
from notify_api.db.models.notification import NotificationModel
from tests.utilities.factory_scenarios import NOTIFICATION_DATA


def test_find_notification_by_id(session, loop):
    """Assert the test can retrieve notification by id."""
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    result = loop.run_until_complete(
        NotificaitonCRUD.find_notification_by_id(session, notification.id)
    )
    assert result == notification
    assert result.id == NOTIFICATION_DATA[0]['id']
    assert result.recipients == NOTIFICATION_DATA[0]['recipients']


def test_find_notification_by_status(session, loop):
    """Assert the test can retrieve notifications by status."""
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    result = loop.run_until_complete(
        NotificaitonCRUD.find_notifications_by_status(session, notification.status_code)
    )
    assert result[0] == notification
    assert result[0].id == NOTIFICATION_DATA[0]['id']
    assert result[0].recipients == NOTIFICATION_DATA[0]['recipients']


def test_find_notification_by_status_time(session, loop):
    """Assert the test can retrieve notifications by status and time frame."""
    notification = NotificationModel(**NOTIFICATION_DATA[3])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    result = loop.run_until_complete(
        NotificaitonCRUD.find_notifications_by_status_time(session, notification.status_code, 1)
    )
    assert result[0] == notification
    assert result[0].id == NOTIFICATION_DATA[3]['id']
    assert result[0].recipients == NOTIFICATION_DATA[3]['recipients']


def test_create_notification(session, loop):
    """Assert the test can create notification."""
    result = loop.run_until_complete(
        NotificaitonCRUD.create_notification(session, NotificationModel(**NOTIFICATION_DATA[0]))
    )
    assert result.id == NOTIFICATION_DATA[0]['id']
    assert result.recipients == NOTIFICATION_DATA[0]['recipients']


def test_update_notification(session, loop):
    """Assert the test can update notification."""
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    notification.sent_date = datetime.now()
    notification.status_code = 'FAILURE'
    result = loop.run_until_complete(
        NotificaitonCRUD.update_notification(session, notification)
    )
    assert result == notification
    assert result.id == NOTIFICATION_DATA[0]['id']
    assert result.recipients == NOTIFICATION_DATA[0]['recipients']
    assert result.status_code == 'FAILURE'
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
import logging
from datetime import datetime

from notify_api.db.models.notification import NotificationRequest, NotificationUpdate
from notify_api.services.notify import NotifyService
from tests.factories.attachment import AttachmentFactory
from tests.factories.content import ContentFactory
from tests.factories.notification import NotificationFactory


logger = logging.getLogger(__name__)


def test_find_notification_by_id(session, loop):
    """Assert the test can retrieve notification by id."""
    notification = NotificationFactory.create_model(session, notification_info=NotificationFactory.Models.PENDING_1)
    content = ContentFactory.create_model(session, notification.id, content_info=ContentFactory.Models.CONTENT_1)
    AttachmentFactory.create_model(session, content.id, attachment_info=AttachmentFactory.Models.FILE_1)

    result = loop.run_until_complete(
        NotifyService.find_notification(session, notification.id)
    )

    assert result.id == NotificationFactory.Models.PENDING_1['id']
    assert result.recipients == NotificationFactory.Models.PENDING_1['recipients']
    assert result.content.subject == ContentFactory.Models.CONTENT_1['subject']
    assert result.content.attachments[0].file_name == AttachmentFactory.Models.FILE_1['file_name']


def test_find_notification_by_status(session, loop):
    """Assert the test can retrieve notification by status."""
    notification = NotificationFactory.create_model(session)

    result = loop.run_until_complete(
        NotifyService.find_notifications_by_status(session, notification.status_code)
    )
    assert result[0].id == NotificationFactory.Models.PENDING_1['id']
    assert result[0].recipients == NotificationFactory.Models.PENDING_1['recipients']


def test_find_notification_by_status_time(session, loop):
    """Assert the test can retrieve notification by status and time frame."""
    notification = NotificationFactory.create_model(session,
                                                    notification_info=NotificationFactory.Models.LESS_1_HOUR)

    result = loop.run_until_complete(
        NotifyService.find_notifications_by_status(session, notification.status_code)
    )
    assert result[0] == notification
    assert result[0].id == NotificationFactory.Models.LESS_1_HOUR['id']
    assert result[0].recipients == NotificationFactory.Models.LESS_1_HOUR['recipients']


def test_find_no_notification_by_status_time(session, loop):
    """Assert the test can not retrieve notification by status and time frame."""
    notification = NotificationFactory.create_model(session,
                                                    notification_info=NotificationFactory.Models.OVER_1_HOUR)

    result = loop.run_until_complete(
        NotifyService.find_notifications_by_status(session, notification.status_code)
    )
    assert not result


def test_create_notification(session, loop, client, client_id, stan_server):  # pylint: disable=unused-argument
    """Assert the test can create notification."""
    result = loop.run_until_complete(
        NotifyService.send_notification(session, NotificationRequest(**NotificationFactory.RequestData.REQUEST_1))
    )
    assert result is not None
    assert result.recipients == NotificationFactory.RequestData.REQUEST_1['recipients']


def test_update_notification(session, loop):
    """Assert the test can update notification."""
    notification = NotificationFactory.create_model(session)

    update_notification: NotificationUpdate = NotificationUpdate(id=notification.id,
                                                                 sent_date=datetime.now(),
                                                                 notify_status='FAILURE')
    result = loop.run_until_complete(
        NotifyService.update_notification_status(session, update_notification)
    )

    assert result.id == NotificationFactory.Models.PENDING_1['id']
    assert result.recipients == NotificationFactory.Models.PENDING_1['recipients']
    assert result.status_code == 'FAILURE'


def test_update_notification_success(session, loop):
    """Assert the test can update notification."""
    notification = NotificationFactory.create_model(session)
    ContentFactory.create_model(session, notification.id, content_info=ContentFactory.Models.CONTENT_1)

    update_notification: NotificationUpdate = NotificationUpdate(id=notification.id,
                                                                 sent_date=datetime.now(),
                                                                 notify_status='DELIVERED')
    result = loop.run_until_complete(
        NotifyService.update_notification_status(session, update_notification)
    )

    assert result.id == NotificationFactory.Models.PENDING_1['id']
    assert result.recipients == NotificationFactory.Models.PENDING_1['recipients']
    assert result.status_code == 'DELIVERED'
    assert result.content.body == ''


def test_update_notification_no_exists(session, loop):
    """Assert the test can not update a non exists notification."""
    update_notification: NotificationUpdate = NotificationUpdate(id=999,
                                                                 sent_date=datetime.now(),
                                                                 notify_status='FAILURE')
    result = loop.run_until_complete(
        NotifyService.update_notification_status(session, update_notification)
    )
    assert result is None

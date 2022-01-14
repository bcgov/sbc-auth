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
import logging

from notify_api.db.crud import attachment as AttachmentCRUD
from notify_api.db.crud import content as ContentCRUD
from notify_api.db.models.content import ContentRequest
from tests.factories.attachment import AttachmentFactory
from tests.factories.content import ContentFactory
from tests.factories.notification import NotificationFactory


logger = logging.getLogger(__name__)


def test_find_content_by_id(session, loop):
    """Assert the test can retrieve notification contents with id."""
    notification = NotificationFactory.create_model(session, notification_info=NotificationFactory.Models.PENDING_1)
    content = ContentFactory.create_model(session, notification.id, content_info=ContentFactory.Models.CONTENT_1)

    result = loop.run_until_complete(
        ContentCRUD.find_content_by_id(session, content.id)
    )

    assert result.id == ContentFactory.Models.CONTENT_1['id']
    assert result.subject == ContentFactory.Models.CONTENT_1['subject']


def test_find_content_by_notification_id(session, loop):
    """Assert the test can retrieve notification contents with notification id."""
    notification = NotificationFactory.create_model(session, notification_info=NotificationFactory.Models.PENDING_1)
    ContentFactory.create_model(session, notification.id, content_info=ContentFactory.Models.CONTENT_1)

    result = loop.run_until_complete(
        ContentCRUD.find_content_by_notification_id(session, notification.id)
    )
    assert result.id == ContentFactory.Models.CONTENT_1['id']
    assert result.subject == ContentFactory.Models.CONTENT_1['subject']


def test_create_contents(session, loop):
    """Assert the test can create notification contents."""
    notification = NotificationFactory.create_model(session, notification_info=NotificationFactory.Models.PENDING_1)

    request_content: ContentRequest = ContentRequest(**ContentFactory.RequestData.CONTENT_REQUEST_1)

    result = loop.run_until_complete(
        ContentCRUD.create_content(session, request_content, notification_id=notification.id)
    )

    assert result.subject == ContentFactory.RequestData.CONTENT_REQUEST_1['subject']


def test_create_contents_with_attachment(session, loop):
    """Assert the test can create notification contents with attachment."""
    notification = NotificationFactory.create_model(session, notification_info=NotificationFactory.Models.PENDING_1)

    request_content: ContentRequest = ContentRequest(**ContentFactory.RequestData.CONTENT_REQUEST_2)

    result = loop.run_until_complete(
        ContentCRUD.create_content(session, request_content, notification_id=notification.id)
    )

    assert result.subject == ContentFactory.RequestData.CONTENT_REQUEST_2['subject']

    result_attachment = loop.run_until_complete(
        AttachmentCRUD.find_attachments_by_content_id(session, result.id)
    )

    assert result_attachment[0].file_name == AttachmentFactory.RequestData.FILE_REQUEST_1['fileName']


def test_create_contents_with_attachment_url(session, loop):
    """Assert the test can create notification contents with attachment url."""
    notification = NotificationFactory.create_model(session, notification_info=NotificationFactory.Models.PENDING_1)

    request_content: ContentRequest = ContentRequest(**ContentFactory.RequestData.CONTENT_REQUEST_3)

    result = loop.run_until_complete(
        ContentCRUD.create_content(session, request_content, notification_id=notification.id)
    )

    assert result.subject == ContentFactory.RequestData.CONTENT_REQUEST_3['subject']

    result_attachment = loop.run_until_complete(
        AttachmentCRUD.find_attachments_by_content_id(session, result.id)
    )

    assert result_attachment[0].file_name == AttachmentFactory.RequestData.FILE_REQUEST_1['fileName']
    assert result_attachment[1].file_name == AttachmentFactory.RequestData.FILE_REQUEST_2['fileName']


def test_update_content(session, loop):
    """Assert the test can update content."""
    notification = NotificationFactory.create_model(session, notification_info=NotificationFactory.Models.PENDING_1)

    content = ContentFactory.create_model(session, notification.id, content_info=ContentFactory.Models.CONTENT_1)

    content.body = ''
    result = loop.run_until_complete(
        ContentCRUD.update_content(session, content)
    )

    assert result.notification_id == NotificationFactory.Models.PENDING_1['id']
    assert result.body == ''

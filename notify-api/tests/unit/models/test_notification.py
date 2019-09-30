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
"""Tests for the Notification model.

Test suite to ensure that the  model routines are working as expected.
"""

from _datetime import datetime
from notify_api.models import Notification as NotificationModel


def factory_notification_model():
    """Produce a templated notification model."""
    notification = NotificationModel()
    notification.recipients = 'abc@test.com'
    notification.request_date = datetime.now()
    notification.type_code = 'EMAIL'
    notification.status_code = 'PENDING'

    notification.save()
    return notification


def test_create_notification(session):
    """Assert that an Notification can be stored in the service."""
    notification = factory_notification_model()
    session.add(notification)
    session.commit()
    assert notification.id is not None


def test_create_from_dict(session):  # pylint:disable=unused-argument
    """Assert that an Notification can be stored in the service."""
    notify_info = {
        'notifyType': 'EMAIL',
        'requestDate': '2019-09-25T09:08:57.515479+00:00',
        'subject': 'test email',
        'recipients': 'test@abc.com',
        'contentBody': 'This is a test email from notify service.'
    }
    notification = NotificationModel.create_from_dict(notify_info)
    assert notification.id is not None


def test_create_from_dict_without_content(session):  # pylint:disable=unused-argument
    """Assert that an Notification can be stored in the service."""
    notify_info = None
    notification = NotificationModel.create_from_dict(notify_info)
    assert notification is None


def test_notification_find_by_id(session):  # pylint:disable=unused-argument
    """Assert that an Notification can retrieved by its id."""
    notification = factory_notification_model()
    session.add(notification)
    session.commit()

    retrieved_notification = NotificationModel.find_by_notification_id(notification.id)
    assert retrieved_notification
    assert retrieved_notification.id == notification.id

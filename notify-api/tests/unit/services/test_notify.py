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
"""Tests for the Invitation service.

Test suite to ensure that the Invitation service routines are working as expected.
"""

import pytest

from notify_api.exceptions import NotifyException
from notify_api.exceptions.errors import Error
from notify_api.services import Notify as NotifyService


def test_create_notification(session):  # pylint:disable=unused-argument
    """Assert that a Notification can be created."""
    notify_info = {
        'notifyType': 'EMAIL',
        'requestDate': '2019-09-25T09:08:57.515479+00:00',
        'subject': 'test email',
        'recipients': 'test@abc.com',
        'contentBody': 'This is a test email from notify service.'
    }
    notification = NotifyService.create_notification(notify_info)
    notification_dictionary = notification.as_dict()
    assert notification_dictionary['recipients'] == notify_info['recipients']
    assert notification_dictionary['id']
    assert notification_dictionary['notificationStatus'] == 'SUCCESS'


def test_create_notification_pending(session):  # pylint:disable=unused-argument
    """Assert that a Notification can be created and could not be send."""
    notify_info = {
        'notifyType': 'TEXT',
        'requestDate': '2019-09-25T09:08:57.515479+00:00',
        'subject': 'test email',
        'recipients': 'test@abc.com',
        'contentBody': 'This is a test email from notify service.'
    }
    notification = NotifyService.create_notification(notify_info)
    notification_dictionary = notification.as_dict()
    assert notification_dictionary['recipients'] == notify_info['recipients']
    assert notification_dictionary['id']
    assert notification_dictionary['notificationStatus'] == 'PENDING'


def test_create_notification_fail(session):  # pylint:disable=unused-argument
    """Assert that a Notification can be created and could not be send."""
    notify_info = {
        'notifyType': 'EMAIL',
        'requestDate': '2019-09-25T09:08:57.515479+00:00',
        'subject': 'test email',
        'recipients': ' ',
        'contentBody': 'This is a test email from notify service.'
    }

    notification = NotifyService.create_notification(notify_info)

    notification_dictionary = notification.as_dict()
    assert notification_dictionary['id']
    assert notification_dictionary['notificationStatus'] == 'FAILURE'


def test_get_notifications(session):  # pylint:disable=unused-argument
    """Assert that a Notification can be retrieved."""
    notify_info = {
        'notifyType': 'EMAIL',
        'requestDate': '2019-09-25T09:08:57.515479+00:00',
        'subject': 'test email',
        'recipients': 'test@abc.com',
        'contentBody': 'This is a test email from notify service.'
    }
    notification = NotifyService.create_notification(notify_info)
    notification_dictionary = notification.as_dict()
    notification = NotifyService.get_notification(notification_dictionary['id'])
    notification_dictionary = notification.as_dict()
    assert notification_dictionary['recipients'] == notify_info['recipients']


def test_send_email(session):  # pylint:disable=unused-argument
    """Assert that a Notification can be sent by email."""
    notify_info = {
        'notifyType': 'EMAIL',
        'requestDate': '2019-09-25T09:08:57.515479+00:00',
        'subject': 'test email',
        'recipients': 'test@abc.com',
        'contentBody': 'This is a test email from notify service.'
    }
    NotifyService.send_email(notify_info)


def test_send_email_exception(session):  # pylint:disable=unused-argument
    """Assert that a Notification can be sent by email but failed."""
    notify_info = {
        'notifyType': 'EMAIL',
        'requestDate': '2019-09-25T09:08:57.515479+00:00',
    }

    with pytest.raises(NotifyException) as excinfo:
        NotifyService.send_email(notify_info)

        assert excinfo.value.status_code == Error.SEND_EMAIL_FAIL.status_code
        assert excinfo.value.message == Error.SEND_EMAIL_FAIL.message

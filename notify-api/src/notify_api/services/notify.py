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

from datetime import datetime

from flask import current_app
from flask_mail import Message

from notify_api.exceptions import NotifyException
from notify_api.exceptions.errors import Error
from notify_api.extensions import mail
from notify_api.models import Notification as NotificationModel
from notify_api.schemas import NotifySchema
from notify_api.utils.enums import NotificationStatus, NotificationType
from sbc_common_components.tracing.service_tracing import ServiceTracing


class Notify:  # pylint: disable=too-few-public-methods
    """Class that manages notification."""

    def __init__(self, model):
        """Return a Notification service instance."""
        self._model = model

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the internal Notification model as a dictionary."""
        notify_schema = NotifySchema()
        obj = notify_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    def create_notification(notify_info: dict):
        """Create a new notification and send it out."""
        notification = NotificationModel.create_from_dict(notify_info)
        if notification.type_code == NotificationType.EMAIL.value:
            try:
                # sent email success then update the status
                Notify.send_email(notify_info)
                notification.sent_date = datetime.now()
                notification.status_code = NotificationStatus.SUCCESS.value
            except NotifyException:
                notification.status_code = NotificationStatus.FAILURE.value
            notification.save()
        return Notify(notification)

    @staticmethod
    def get_notification(notification_id):
        """Get notification by an id."""
        notification = NotificationModel.find_by_notification_id(notification_id)
        return Notify(notification)

    @staticmethod
    def send_email(notify_info: NotifySchema):
        """Send the email using the given details."""
        try:
            sender = current_app.config.get('MAIL_FROM_ID')
            msg = Message(notify_info['subject'], sender=sender, recipients=notify_info['recipients'].split())
            msg.html = notify_info['contentBody']
            mail.send(msg)
        except Exception as exception:
            current_app.logger.error('Send email fail {}'.format(exception))
            raise NotifyException(Error.SEND_EMAIL_FAIL, exception)

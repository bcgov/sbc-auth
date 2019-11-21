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
"""The unique worker functionality for this service is contained here.

The entry-point is the **cb_subscription_handler**

The design and flow leverage a few constraints that are placed upon it
by NATS Streaming and using AWAIT on the default loop.
- NATS streaming queues require one message to be processed at a time.
- AWAIT on the default loop effectively runs synchronously

If these constraints change, the use of Flask-SQLAlchemy would need to change.
Flask-SQLAlchemy currently allows the base model to be changed, or reworking
the model to a standalone SQLAlchemy usage with an async engine would need
to be pursued.
"""
import json
import re
import unicodedata
from datetime import datetime
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import nats
from aiosmtplib import SMTP
from entity_queue_common.service import QueueServiceManager
from entity_queue_common.service_utils import QueueException, logger
from notify_api import NotifyAPI
from notify_api.core import config as app_config
from notify_api.db.models.notification import Notification, NotificationUpdate
from notify_api.db.models.notification_status import NotificationStatusEnum
from notify_api.services.notify import NotifyService
from sentry_sdk import capture_message


qsm = QueueServiceManager()  # pylint: disable=invalid-name
APP = NotifyAPI(bind=app_config.SQLALCHEMY_DATABASE_URI)


async def send_with_send_message(sender, recipients, message):
    """Send email."""
    smtp_client = SMTP(hostname=app_config.MAIL_SERVER, port=app_config.MAIL_PORT)
    await smtp_client.connect()
    await smtp_client.send_message(message=message, recipients=recipients, sender=sender)
    await smtp_client.quit()


async def process_notification(notification_id: int):
    """Send the notification to smtp server."""
    try:
        notification: Notification = await NotifyService.find_notification(APP.db_session, notification_id)
        encoding = 'utf-8'
        message = MIMEMultipart()
        message['Subject'] = notification.contents.subject
        message.attach(MIMEText(notification.contents.body, 'html', encoding))

        if notification.contents.attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(notification.contents.attachment)
            encode_base64(part)

            spaces = re.compile(r'[\s]+', re.UNICODE)
            filename = unicodedata.normalize('NFKD', notification.contents.attachment_name)
            filename = filename.encode('ascii', 'ignore').decode('ascii')
            filename = spaces.sub(u' ', filename).strip()

            try:
                filename and filename.encode('ascii')
            except UnicodeEncodeError:
                filename = ('UTF8', '', filename)

            part.add_header('Content-Disposition', 'attachment; filename=' + filename)

            message.attach(part)

        await send_with_send_message(app_config.MAIL_FROM_ID, notification.recipients.split(','), message)

        update_notification: NotificationUpdate = NotificationUpdate(id=notification_id,
                                                                     sent_date=datetime.utcnow(),
                                                                     notify_status=NotificationStatusEnum.DELIVERED)

        await NotifyService.update_notification_status(APP.db_session, update_notification)
    except Exception as err:  # pylint: disable=broad-except, unused-variable # noqa F841;
        capture_message(f'Notify Service Error: Failied to send email:{notification.recipients} with error:{err}',
                        level='error')
        logger.error('Notify Job (process_notification) Error: %s', exc_info=True)
        update_notification: NotificationUpdate = NotificationUpdate(id=notification_id,
                                                                     sent_date=datetime.utcnow(),
                                                                     notify_status=NotificationStatusEnum.FAILURE)

        await NotifyService.update_notification_status(APP.db_session, update_notification)

    return


async def cb_subscription_handler(msg: nats.aio.client.Msg):
    """Use Callback to process Queue Msg objects."""
    try:
        logger.info('Received raw message seq:%s, data=  %s', msg.sequence, msg.data.decode())
        notification_id = json.loads(msg.data.decode('utf-8'))
        logger.info('Extracted id: %s', notification_id)
        await process_notification(notification_id)
    except (QueueException, Exception):  # pylint: disable=broad-except
        # Catch Exception so that any error is still caught and the message is removed from the queue
        capture_message('Notify Queue Error:', level='error')
        logger.error('Notify Queue Error: %s', exc_info=True)
    finally:
        APP.db_session.close()


async def job_handler(status: str):
    """Use schedule task to process notifications from db."""
    try:
        logger.info('Schedule Job for sending %s email run at:%s', status, datetime.utcnow())
        notifications = await NotifyService.find_notifications_by_status(APP.db_session, status)
        for notification in notifications:
            logger.info('Process notificaiton id: %s', notification.id)
            await process_notification(notification.id)
        logger.info('Schedule Job for sending %s email finish at:%s', status, datetime.utcnow())
    except Exception:  # pylint: disable=broad-except
        # Catch Exception so that any error is still caught and the message is removed from the queue
        capture_message('Notify Job Error:', level='error')
        logger.error('Notify Job Error: %s', exc_info=True)
    finally:
        APP.db_session.close()
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
"""The unique worker functionality for this service is contained here."""
import json
import logging.config
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
from entity_queue_common.service_utils import QueueException
from notify_api import NotifyAPI
from notify_api.db.models.notification import Notification, NotificationUpdate
from notify_api.db.models.notification_status import NotificationStatusEnum
from notify_api.services.notify import NotifyService

from notify_service import config as app_config


# setup loggers
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

qsm = QueueServiceManager()  # pylint: disable=invalid-name
APP = NotifyAPI(bind=app_config.SQLALCHEMY_DATABASE_URI)


async def send_with_send_message(message, recipients):
    """Send email."""
    try:
        smtp_client = SMTP(hostname=app_config.MAIL_SERVER, port=app_config.MAIL_PORT)
        await smtp_client.connect()
        await smtp_client.send_message(message=message, recipients=recipients)
        await smtp_client.quit()
    except Exception as err:  # pylint: disable=broad-except # noqa F841;
        logger.error('Notify Job (send_with_send_message) Error: %s', err)
        return False
    return True


async def process_notification(notification_id: int, db_session):
    """Send the notification to smtp server."""
    try:
        notification: Notification = await NotifyService.find_notification(db_session, notification_id)
        if not notification.status_code == NotificationStatusEnum.DELIVERED:
            sender: str = app_config.MAIL_FROM_ID
            recipients: [] = [s.strip() for s in notification.recipients.split(',')]

            encoding = 'utf-8'
            message = MIMEMultipart()
            message['Subject'] = notification.content.subject
            message['From'] = sender
            message['To'] = notification.recipients
            message.attach(MIMEText(notification.content.body, 'html', encoding))

            if notification.content.attachments:
                for attachment in notification.content.attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.file_bytes)
                    encode_base64(part)

                    spaces = re.compile(r'[\s]+', re.UNICODE)
                    filename = unicodedata.normalize('NFKD', attachment.file_name)
                    filename = filename.encode('ascii', 'ignore').decode('ascii')
                    filename = spaces.sub(' ', filename).strip()

                    try:
                        filename and filename.encode('ascii')
                    except UnicodeEncodeError:
                        filename = ('UTF8', '', filename)

                    part.add_header('Content-Disposition', 'attachment; filename=' + filename)

                    message.attach(part)

            sent_status = await send_with_send_message(message, recipients)
            if not sent_status:
                raise QueueException('Could not send email through SMTP server.')

            update_notification: NotificationUpdate = NotificationUpdate(id=notification_id,
                                                                         sent_date=datetime.utcnow(),
                                                                         notify_status=NotificationStatusEnum.DELIVERED)

            await NotifyService.update_notification_status(db_session, update_notification)
    except (QueueException, Exception) as err:  # pylint: disable=broad-except
        logger.error('Notify Job (process_notification) Error: %s', err)
        update_notification: NotificationUpdate = NotificationUpdate(id=notification_id,
                                                                     sent_date=datetime.utcnow(),
                                                                     notify_status=NotificationStatusEnum.FAILURE)

        await NotifyService.update_notification_status(db_session, update_notification)
    return


async def cb_subscription_handler(msg: nats.aio.client.Msg):
    """Use Callback to process Queue Msg objects."""
    db_session = APP.db_session
    try:
        logger.info('Received raw message seq:%s, data=  %s', msg.sequence, msg.data.decode())
        notification_id = json.loads(msg.data.decode('utf-8'))
        logger.info('Extracted id: %s', notification_id)
        await process_notification(notification_id, db_session)
    except (QueueException, Exception) as err:  # pylint: disable=broad-except
        logger.error('Notify Queue Error: %s', err)
    finally:
        db_session.close()


async def job_handler(status: str):
    """Use schedule task to process notifications from db."""
    db_session = APP.db_session
    try:
        logger.info('Schedule Job for sending %s email run at:%s', status, datetime.utcnow())
        notifications = await NotifyService.find_notifications_by_status(db_session, status)
        for notification in notifications:
            logger.info('Process notificaiton id: %s', notification.id)
            await process_notification(notification.id, db_session)
        logger.info('Schedule Job for sending %s email finish at:%s', status, datetime.utcnow())
    except Exception:  # pylint: disable=broad-except
        logger.info('Notify Job Error: %s', exc_info=True)
    finally:
        db_session.close()

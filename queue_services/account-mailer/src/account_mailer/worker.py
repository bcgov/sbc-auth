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
import os

import nats
from auth_api.models import db
from auth_api.services import notification as notification_service
from entity_queue_common.service import QueueServiceManager
from entity_queue_common.service_utils import QueueException, logger
from flask import Flask  # pylint: disable=wrong-import-order

from account_mailer import config
from account_mailer.email_processors import payment_completed  # pylint: disable=wrong-import-order
from account_mailer.email_processors import refund_requested  # pylint: disable=wrong-import-order


qsm = QueueServiceManager()  # pylint: disable=invalid-name
APP_CONFIG = config.get_named_config(os.getenv('DEPLOYMENT_ENV', 'production'))
FLASK_APP = Flask(__name__)
FLASK_APP.config.from_object(APP_CONFIG)
db.init_app(FLASK_APP)


async def process_event(event_message: dict, flask_app):
    """Process the incoming queue event message."""
    if not flask_app:
        raise QueueException('Flask App not available.')

    with flask_app.app_context():
        message_type = event_message.get('type', None)
        email_msg = None
        email_dict = None
        if message_type == 'account.mailer':
            email_msg = json.loads(event_message.get('data'))
            email_dict = payment_completed.process(email_msg)

        elif message_type == 'bc.registry.payment.refundRequest':
            email_msg = json.loads(event_message.get('data'))
            email_dict = refund_requested.process(email_msg)

        logger.debug('Extracted email msg: %s', email_dict)
        process_email(email_dict, FLASK_APP)


def process_email(email_dict: dict, flask_app: Flask):  # pylint: disable=too-many-branches
    """Process the email contained in the message."""
    if not flask_app:
        raise QueueException('Flask App not available.')

    with flask_app.app_context():
        logger.debug('Attempting to process email: %s', email_dict)
        # get type from email
        notification_service.send_email(email_dict['subject'], email_dict['sender'], email_dict['recepients'],
                                        email_dict['html_body'])


async def cb_subscription_handler(msg: nats.aio.client.Msg):
    """Use Callback to process Queue Msg objects."""
    event_message = None
    try:
        logger.info('Received raw message seq:%s, data=  %s', msg.sequence, msg.data.decode())
        event_message = json.loads(msg.data.decode('utf-8'))
        logger.debug('Event Message Received: %s', event_message)
        await process_event(event_message, FLASK_APP)
    except Exception:  # pylint: disable=broad-except
        # Catch Exception so that any error is still caught and the message is removed from the queue
        logger.error('Queue Error: %s', json.dumps(event_message), exc_info=True)

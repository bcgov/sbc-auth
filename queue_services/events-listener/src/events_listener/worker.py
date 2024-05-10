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
from datetime import datetime

import nats
from auth_api.models import Org as OrgModel
from auth_api.models import db
from auth_api.services import Flags
from auth_api.services.queue_publisher import publish
from auth_api.utils.cache import cache
from auth_api.utils.enums import OrgStatus
from entity_queue_common.service import QueueServiceManager
from entity_queue_common.service_utils import QueueException, logger
from flask import Flask  # pylint: disable=wrong-import-order
from sentry_sdk import capture_message

from events_listener import config


qsm = QueueServiceManager()  # pylint: disable=invalid-name
APP_CONFIG = config.get_named_config(os.getenv('DEPLOYMENT_ENV', 'production'))
FLASK_APP = Flask(__name__)
FLASK_APP.config.from_object(APP_CONFIG)
db.init_app(FLASK_APP)
cache.init_app(FLASK_APP)
flag_service = Flags(FLASK_APP)

UNLOCK_ACCOUNT_MESSAGE_TYPE = 'bc.registry.payment.unlockAccount'
LOCK_ACCOUNT_MESSAGE_TYPE = 'bc.registry.payment.lockAccount'


async def process_event(event_message, flask_app):
    """Render the org status."""
    if not flask_app:
        raise QueueException('Flask App not available.')

    with flask_app.app_context():
        message_type = event_message.get('type', None)
        data = event_message.get('data')
        org_id = data.get('accountId')
        org: OrgModel = OrgModel.find_by_org_id(org_id)
        if org is None:
            logger.error('Unknown org for orgid %s', org_id)
            return

        if message_type == LOCK_ACCOUNT_MESSAGE_TYPE:
            org.status_code = OrgStatus.NSF_SUSPENDED.value
            org.suspended_on = datetime.now()
            org.suspension_reason_code = data.get('suspensionReasonCode', None)
            data = {
                'accountId': org_id,
            }
            await publish_mailer_events(LOCK_ACCOUNT_MESSAGE_TYPE, org_id, data)
        elif message_type == UNLOCK_ACCOUNT_MESSAGE_TYPE:
            org.status_code = OrgStatus.ACTIVE.value
            org.suspension_reason_code = None
            await publish_mailer_events(UNLOCK_ACCOUNT_MESSAGE_TYPE, org_id, data)
        else:
            logger.error('Unknown Message Type : %s', message_type)
            return

        org.flush()
        db.session.commit()


async def cb_subscription_handler(msg: nats.aio.client.Msg):
    """Use Callback to process Queue Msg objects."""
    try:
        logger.info('Received raw message seq:%s, data=  %s', msg.sequence, msg.data.decode())
        event_message = json.loads(msg.data.decode('utf-8'))
        logger.debug('Event Message Received: %s', event_message)
        await process_event(event_message, FLASK_APP)
    except Exception:  # noqa pylint: disable=broad-except
        # Catch Exception so that any error is still caught and the message is removed from the queue
        logger.error('Queue Error: %s', json.dumps(event_message), exc_info=True)


async def publish_mailer_events(message_type: str, org_id, data):
    """Publish payment message to the mailer queue."""
    # Publish message to the Queue, saying account has been created. Using the event spec.
    payload = {
        'specversion': '1.x-wip',
        'type': message_type,
        'source': f'https://api.pay.bcregistry.gov.bc.ca/v1/accounts/{org_id}',
        'id': org_id,
        'time': f'{datetime.now()}',
        'datacontenttype': 'application/json',
        'data': data
    }
    try:
        await publish(payload=payload,
                      client_name=APP_CONFIG.NATS_MAILER_CLIENT_NAME,
                      subject=APP_CONFIG.NATS_MAILER_SUBJECT)
    except Exception as e:  # noqa pylint: disable=broad-except
        logger.error(e)
        logger.warning('Notification to Queue failed for the Account Mailer %s - %s', org_id,
                       payload)
        capture_message('Notification to Queue failed for the Account Mailer {auth_account_id}, {msg}.'.format(
            auth_account_id=org_id, msg=payload), level='error')

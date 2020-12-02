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
from auth_api.utils.enums import OrgStatus
from entity_queue_common.service import QueueServiceManager
from entity_queue_common.service_utils import QueueException, logger
from flask import Flask  # pylint: disable=wrong-import-order

from events_listener import config


qsm = QueueServiceManager()  # pylint: disable=invalid-name
APP_CONFIG = config.get_named_config(os.getenv('DEPLOYMENT_ENV', 'production'))
FLASK_APP = Flask(__name__)
FLASK_APP.config.from_object(APP_CONFIG)
db.init_app(FLASK_APP)

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
        elif message_type == UNLOCK_ACCOUNT_MESSAGE_TYPE:
            org.status_code = OrgStatus.ACTIVE.value
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
    except Exception:  # pylint: disable=broad-except
        # Catch Exception so that any error is still caught and the message is removed from the queue
        logger.error('Queue Error: %s', json.dumps(event_message), exc_info=True)

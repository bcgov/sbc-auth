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
from auth_api.models import ActivityLog as ActivityLogModel
from auth_api.models import db
from entity_queue_common.service import QueueServiceManager
from entity_queue_common.service_utils import QueueException, logger
from flask import Flask  # pylint: disable=wrong-import-order

from activity_log_listener import config


qsm = QueueServiceManager()  # pylint: disable=invalid-name
APP_CONFIG = config.get_named_config(os.getenv('DEPLOYMENT_ENV', 'production'))
FLASK_APP = Flask(__name__)
FLASK_APP.config.from_object(APP_CONFIG)
db.init_app(FLASK_APP)


async def process_event(event_message, flask_app):
    """Insert into Activity log table."""
    if not flask_app:
        raise QueueException('Flask App not available.')

    with flask_app.app_context():
        data = event_message.get('data')
        logger.debug('message_type received %s', data)

        activity_model: ActivityLogModel = ActivityLogModel(actor_id=data.get('actorId'),
                                                            action=data.get('action'),
                                                            item_type=data.get('itemType'),
                                                            item_name=data.get('itemName'),
                                                            item_id=data.get('itemId'),
                                                            item_value=data.get('itemValue'),
                                                            remote_addr=data.get('remoteAddr'),
                                                            created=data.get('createdAt'),
                                                            org_id=data.get('orgId')
                                                            )
        try:
            activity_model.save()
            logger.debug('activity log saved')
        except Exception as e:  # NOQA # pylint: disable=broad-except
            logger.error('DB Error: %s', e)
            activity_model.rollback()


async def cb_subscription_handler(msg: nats.aio.client.Msg):
    """Use Callback to process Queue Msg objects."""
    try:
        logger.info('Received raw message seq:%s, data=  %s', msg.sequence, msg.data.decode())
        event_message = json.loads(msg.data.decode('utf-8'))
        logger.debug('Event Message Received: %s', event_message)
        await process_event(event_message, FLASK_APP)
    except Exception:  # noqa: B902 # pylint: disable=broad-except
        # Catch Exception so any error is still caught and the message is removed from the queue
        logger.error('Queue Error: %s', json.dumps(event_message), exc_info=True)

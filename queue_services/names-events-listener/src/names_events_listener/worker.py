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

The entry-point is the **cb_nr_subscription_handler**

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
from typing import Dict

import nats
from auth_api.models import ActivityLog as ActivityModel
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Entity as EntityModel
from auth_api.models import Org as OrgModel
from auth_api.models import db
from auth_api.services import Flags
from auth_api.services.rest_service import RestService
from auth_api.utils.cache import cache
from auth_api.utils.enums import AccessType, ActivityAction, CorpType
from dateutil import parser
from entity_queue_common.service import QueueServiceManager
from entity_queue_common.service_utils import QueueException, logger
from flask import Flask  # pylint: disable=wrong-import-order

from names_events_listener import config


async def cb_nr_subscription_handler(msg: nats.aio.client.Msg):
    """Use Callback to process Queue Msg objects."""
    try:
        logger.info('Received raw message seq:%s, data=  %s', msg.sequence, msg.data.decode())
        event_message = json.loads(msg.data.decode('utf-8'))
        logger.debug('Event Message Received: %s', event_message)
        await process_event(event_message, FLASK_APP)
    except Exception:  # noqa pylint: disable=broad-except
        # Catch Exception so that any error is still caught and the message is removed from the queue
        logger.error('Queue Error: %s', json.dumps(event_message), exc_info=True)


async def process_event(event_message, flask_app):
    """Render the org status."""
    if not flask_app:
        raise QueueException('Flask App not available.')

    with flask_app.app_context():
        message_type = event_message.get('type', None)

        if message_type == 'bc.registry.names.events':
            await process_name_events(event_message)


async def process_name_events(event_message: Dict[str, any]):
    """Process name events.

    1. Check if the NR already exists in entities table, if yes apply changes. If not create entity record.
    2. Check if new status is DRAFT, if yes call pay-api and get the account details for the payments against the NR.
    3. If an account is found, affiliate to that account.

    Args:
        event_message (object): cloud event message, sample below.
            {
                'specversion': '1.0.1',
                'type': 'bc.registry.names.events',
                'source': '/requests/6724165',
                'id': id,
                'time': '',
                'datacontenttype': 'application/json',
                'identifier': '781020202',
                'data': {
                    'request': {
                        'nrNum': 'NR 5659951',
                        'newState': 'APPROVED',
                        'previousState': 'DRAFT'
                    }
                }
            }
    """
    logger.debug('>>>>>>>process_name_events>>>>>')
    request_data = event_message.get('data').get('request') or event_message.get('data').get('name')
    nr_number = request_data['nrNum']
    nr_status = request_data['newState']
    nr_entity = EntityModel.find_by_business_identifier(nr_number)
    if nr_entity is None:
        logger.info("Entity doesn't exist, creating a new entity.")
        nr_entity = EntityModel(
            business_identifier=nr_number,
            corp_type_code=CorpType.NR.value
        )

    nr_entity.status = nr_status
    nr_entity.name = request_data.get('name', '')  # its not part of event now, this is to handle if they include it.
    nr_entity.last_modified_by = None  # TODO not present in event message.
    nr_entity.last_modified = parser.parse(event_message.get('time'))
    # Future - None needs to be replaced with whatever we decide to fill the data with.
    if nr_status == 'DRAFT' and not AffiliationModel.find_affiliations_by_business_identifier(nr_number, None):
        logger.info('Status is DRAFT, getting invoices for account')
        # Find account details for the NR.
        invoices = RestService.get(
            f'{APP_CONFIG.PAY_API_URL}/payment-requests?businessIdentifier={nr_number}',
            token=RestService.get_service_account_token()
        ).json()

        # Ideally there should be only one or two (priority fees) payment request for the NR.
        if invoices and invoices['invoices'] \
                and (auth_account_id := invoices['invoices'][0].get('paymentAccount').get('accountId')) \
                and str(auth_account_id).isnumeric():
            logger.info('Account ID received : %s', auth_account_id)
            # Auth account id can be service account value too, so doing a query lookup than find_by_id
            org: OrgModel = db.session.query(OrgModel).filter(OrgModel.id == auth_account_id).one_or_none()
            # If account is present and is not a gov account, then affiliate.
            if org and org.access_type != AccessType.GOVM.value:
                nr_entity.pass_code_claimed = True
                # Create an affiliation.
                logger.info('Creating affiliation between Entity : %s and Org : %s', nr_entity, org)
                affiliation: AffiliationModel = AffiliationModel(entity=nr_entity, org=org)
                affiliation.flush()
                activity: ActivityModel = ActivityModel(org_id=org.id, action=ActivityAction.CREATE_AFFILIATION.value,
                                                        item_name=nr_entity.business_identifier,
                                                        item_id=nr_entity.business_identifier,
                                                        item_type=None, item_value=None, actor_id=None
                                                        )
                activity.flush()

    nr_entity.save()
    logger.debug('<<<<<<<process_name_events<<<<<<<<<<')


qsm = QueueServiceManager()  # pylint: disable=invalid-name
APP_CONFIG = config.get_named_config(os.getenv('DEPLOYMENT_ENV', 'production'))
FLASK_APP = Flask(__name__)
FLASK_APP.config.from_object(APP_CONFIG)
db.init_app(FLASK_APP)
cache.init_app(FLASK_APP)
flag_service = Flags(FLASK_APP)

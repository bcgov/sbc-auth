# Copyright © 2024 Province of British Columbia
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
"""The unique worker functionality for this service is contained here."""
import dataclasses
import json
from datetime import datetime, timezone
from http import HTTPStatus

from auth_api.models import ActivityLog as ActivityLogModel
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Entity as EntityModel
from auth_api.models import Org as OrgModel
from auth_api.models import db
from auth_api.models.pubsub_message_processing import PubSubMessageProcessing
from auth_api.services.gcp_queue import queue
from auth_api.services.gcp_queue.gcp_auth import ensure_authorized_queue_user
from auth_api.services.rest_service import RestService
from auth_api.utils.account_mailer import publish_to_mailer
from auth_api.utils.enums import AccessType, ActivityAction, CorpType, OrgStatus, QueueSources
from dateutil import parser
from flask import Blueprint, current_app, request
from sbc_common_components.utils.enums import QueueMessageTypes
from simple_cloudevent import SimpleCloudEvent
from structured_logging import StructuredLogging


bp = Blueprint('worker', __name__)

logger = StructuredLogging.get_logger()


@bp.route('/', methods=('POST',))
@ensure_authorized_queue_user
def worker():
    """Worker to handle incoming queue pushes."""
    if not (event_message := queue.get_simple_cloud_event(request, wrapped=True)):
        # Return a 200, so event is removed from the Queue
        return {}, HTTPStatus.OK

    try:
        logger.info('Event message received: %s', json.dumps(dataclasses.asdict(event_message)))
        if is_message_processed(event_message):
            logger.info('Event message already processed, skipping.')
            return {}, HTTPStatus.OK
        if event_message.type == QueueMessageTypes.NAMES_EVENT.value:
            process_name_events(event_message)
        elif event_message.type == QueueMessageTypes.ACTIVITY_LOG.value:
            process_activity_log(event_message.data)
        elif event_message.type in [QueueMessageTypes.NSF_UNLOCK_ACCOUNT.value,
                                    QueueMessageTypes.NSF_LOCK_ACCOUNT.value]:
            process_pay_lock_unlock_event(event_message)
    except Exception: # NOQA # pylint: disable=broad-except
        logger.error('Error processing event:', exc_info=True)
    # Return a 200, so the event is removed from the Queue
    return {}, HTTPStatus.OK


def is_message_processed(event_message):
    """Check if the queue message is processed."""
    if PubSubMessageProcessing.find_by_cloud_event_id_and_type(event_message.id, event_message.type):
        return True
    pubsub_message_processing = PubSubMessageProcessing()
    pubsub_message_processing.cloud_event_id = event_message.id
    pubsub_message_processing.message_type = event_message.type
    pubsub_message_processing.processed = datetime.now(timezone.utc)
    db.session.add(pubsub_message_processing)
    db.session.commit()
    return False


def process_activity_log(data):
    """Process activity log events."""
    logger.debug('>>>>>>>process_activity_log>>>>>')
    activity_model = ActivityLogModel(actor_id=data.get('actorId'),
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
    except Exception as e:  # NOQA # pylint: disable=broad-except
        logger.error('DB Error: %s', e)
        db.session.rollback()
    logger.debug('<<<<<<<process_activity_log<<<<<')


def process_pay_lock_unlock_event(event_message: SimpleCloudEvent):
    """Process a pay event to either unlock or lock an account. Source message comes from Pay-api."""
    logger.debug('>>>>>>>process_pay_lock_unlock_event>>>>>')
    message_type = event_message.type
    queue_data = event_message.data
    skip_notification = queue_data.get('skipNotification', False)
    org_id = queue_data.get('accountId')
    org: OrgModel = OrgModel.find_by_org_id(org_id)
    if org is None:
        logger.error('Unknown org for orgid %s', org_id)
        return

    data = {
        'accountId': org_id,
    }
    if message_type == QueueMessageTypes.NSF_LOCK_ACCOUNT.value:
        org.status_code = OrgStatus.NSF_SUSPENDED.value
        org.suspended_on = datetime.now()
        org.suspension_reason_code = queue_data.get('suspensionReasonCode', None)
        data['additionalEmails'] = queue_data.get('additionalEmails', None)
        if skip_notification is False:
            publish_to_mailer(QueueMessageTypes.NSF_LOCK_ACCOUNT.value, data, QueueSources.AUTH_QUEUE.value)
    elif message_type == QueueMessageTypes.NSF_UNLOCK_ACCOUNT.value:
        org.status_code = OrgStatus.ACTIVE.value
        org.suspension_reason_code = None
        if skip_notification is False:
            # Unlock requires a significant amount of data to generate a receipt, just carry forward queue data.
            publish_to_mailer(QueueMessageTypes.NSF_UNLOCK_ACCOUNT.value, queue_data, QueueSources.AUTH_QUEUE.value)

    org.flush()
    db.session.commit()
    logger.debug('<<<<<<<process_pay_lock_unlock_event<<<<<')


def process_name_events(event_message: SimpleCloudEvent):
    """Process name events.

    1. Check if the NR already exists in entities table, if yes apply changes. If not create entity record.
    2. Check if new status is DRAFT, if yes call pay-api and get the account details for the payments against the NR.
    3. If an account is found, affiliate to that account.

    Args:
        event_message (object): cloud event message, sample below.
            {
                'type': 'bc.registry.names.events',
                'id': id,
                'time': '',
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
    request_data = event_message.data.get('request') or event_message.data.get('name')
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
    nr_entity.last_modified = parser.parse(event_message.time)
    # Future - None needs to be replaced with whatever we decide to fill the data with.
    if nr_status == 'DRAFT' and not AffiliationModel.find_affiliations_by_business_identifier(nr_number, None):
        logger.info('Status is DRAFT, getting invoices for account')
        token = None
        # Find account details for the NR.
        with current_app.test_request_context('service_token'):
            token = RestService.get_service_account_token()
        invoices = RestService.get(
            f'{current_app.config.get("PAY_API_URL")}/payment-requests?businessIdentifier={nr_number}',
            token=token
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
                logger.info('Creating affiliation between Entity : %s and Org : %s', nr_entity, org)
                affiliation: AffiliationModel = AffiliationModel(entity=nr_entity, org=org)
                affiliation.flush()
                activity: ActivityLogModel = ActivityLogModel(org_id=org.id,
                                                              action=ActivityAction.CREATE_AFFILIATION.value,
                                                              item_name=nr_entity.business_identifier,
                                                              item_id=nr_entity.business_identifier,
                                                              item_type=None, item_value=None, actor_id=None
                                                              )
                activity.flush()

    nr_entity.save()
    logger.debug('<<<<<<<process_name_events<<<<<<<<<<')

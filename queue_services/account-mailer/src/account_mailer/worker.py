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
from auth_api.models import db
from auth_api.services import Flags
from auth_api.services.rest_service import RestService
from auth_api.utils.roles import ADMIN, COORDINATOR
from entity_queue_common.service import QueueServiceManager
from entity_queue_common.service_utils import QueueException, logger
from flask import Flask  # pylint: disable=wrong-import-order

from account_mailer import config  # pylint: disable=wrong-import-order
from account_mailer.auth_utils import get_member_emails
from account_mailer.email_processors import common_mailer  # pylint: disable=wrong-import-order
from account_mailer.email_processors import ejv_failures  # pylint: disable=wrong-import-order
from account_mailer.email_processors import pad_confirmation  # pylint: disable=wrong-import-order
from account_mailer.email_processors import payment_completed  # pylint: disable=wrong-import-order
from account_mailer.email_processors import refund_requested  # pylint: disable=wrong-import-order
from account_mailer.enums import Constants, MessageType, SubjectType, TemplateType, TitleType
from account_mailer.services import minio_service  # pylint: disable=wrong-import-order
from account_mailer.services import notification_service  # pylint: disable=wrong-import-order
from account_mailer.utils import format_currency, get_local_formatted_date  # pylint: disable=wrong-import-order


qsm = QueueServiceManager()  # pylint: disable=invalid-name
APP_CONFIG = config.get_named_config(os.getenv('DEPLOYMENT_ENV', 'production'))
FLASK_APP = Flask(__name__)
FLASK_APP.config.from_object(APP_CONFIG)
db.init_app(FLASK_APP)
flag_service = Flags(FLASK_APP)


# pylint: disable=too-many-statements, too-many-branches, too-many-locals
async def process_event(event_message: dict, flask_app):
    """Process the incoming queue event message."""
    if not flask_app:
        raise QueueException('Flask App not available.')

    with flask_app.app_context():
        message_type = event_message.get('type', None)
        email_msg = event_message.get('data')
        logo_url = email_msg['logo_url'] = minio_service.MinioService.get_minio_public_url('bc_logo_for_email.png')
        email_dict = None
        token = RestService.get_service_account_token()
        logger.debug('message_type recieved %s', message_type)
        if message_type == 'account.mailer':
            email_dict = payment_completed.process(email_msg)
        elif message_type in ([MessageType.REFUND_DIRECT_PAY_REQUEST.value, MessageType.REFUND_DRAWDOWN_REQUEST.value]):
            email_dict = refund_requested.process(event_message)
        elif message_type == MessageType.PAD_ACCOUNT_CREATE.value:
            email_msg['registry_logo_url'] = minio_service.MinioService.get_minio_public_url('bc_registry_logo_pdf.svg')
            email_dict = pad_confirmation.process(email_msg, token)
        elif message_type == MessageType.NSF_LOCK_ACCOUNT.value:
            logger.debug('lock account message recieved:')
            template_name = TemplateType.NSF_LOCK_ACCOUNT_TEMPLATE_NAME.value
            org_id = email_msg.get('accountId')
            admin_coordinator_emails = get_member_emails(org_id, (ADMIN, COORDINATOR))
            subject = SubjectType.NSF_LOCK_ACCOUNT_SUBJECT.value
            logo_url = email_msg.get('logo_url')
            email_dict = common_mailer.process(org_id, admin_coordinator_emails, template_name,
                                               subject, logo_url=logo_url)
        elif message_type == MessageType.NSF_UNLOCK_ACCOUNT.value:
            logger.debug('unlock account message recieved')
            template_name = TemplateType.NSF_UNLOCK_ACCOUNT_TEMPLATE_NAME.value
            org_id = email_msg.get('accountId')
            admin_coordinator_emails = get_member_emails(org_id, (ADMIN, COORDINATOR))
            subject = SubjectType.NSF_UNLOCK_ACCOUNT_SUBJECT.value
            logo_url = email_msg.get('logo_url')
            email_dict = common_mailer.process(org_id, admin_coordinator_emails,
                                               template_name, subject, logo_url=logo_url)
        elif message_type == MessageType.ACCOUNT_CONFIRMATION_PERIOD_OVER.value:
            template_name = TemplateType.ACCOUNT_CONF_OVER_TEMPLATE_NAME.value
            org_id = email_msg.get('accountId')
            nsf_fee = format_currency(email_msg.get('nsfFee'))
            admin_coordinator_emails = get_member_emails(org_id, (ADMIN,))
            subject = SubjectType.ACCOUNT_CONF_OVER_SUBJECT.value
            logo_url = email_msg.get('logo_url')
            email_dict = common_mailer.process(org_id, admin_coordinator_emails, template_name, subject,
                                               nsf_fee=nsf_fee, logo_url=logo_url)
        elif message_type in (MessageType.TEAM_MODIFIED.value, MessageType.TEAM_MEMBER_INVITED.value):
            logger.debug('Team Modified message received')
            template_name = TemplateType.TEAM_MODIFIED_TEMPLATE_NAME.value
            org_id = email_msg.get('accountId')
            admin_coordinator_emails = get_member_emails(org_id, (ADMIN,))
            subject = SubjectType.TEAM_MODIFIED_SUBJECT.value
            logo_url = email_msg.get('logo_url')
            email_dict = common_mailer.process(org_id, admin_coordinator_emails, template_name,
                                               subject, logo_url=logo_url)
        elif message_type == MessageType.ADMIN_REMOVED.value:
            logger.debug('ADMIN_REMOVED message received')
            template_name = TemplateType.ADMIN_REMOVED_TEMPLATE_NAME.value
            org_id = email_msg.get('accountId')
            recipient_email = email_msg.get('recipientEmail')
            subject = SubjectType.ADMIN_REMOVED_SUBJECT.value
            logo_url = email_msg.get('logo_url')
            email_dict = common_mailer.process(org_id, recipient_email, template_name,
                                               subject, logo_url=logo_url)
        elif message_type == MessageType.PAD_INVOICE_CREATED.value:
            template_name = TemplateType.PAD_INVOICE_CREATED_TEMPLATE_NAME.value
            org_id = email_msg.get('accountId')
            admin_coordinator_emails = get_member_emails(org_id, (ADMIN,))
            subject = SubjectType.PAD_INVOICE_CREATED.value
            invoice_process_date = datetime.fromisoformat(email_msg.get('invoice_process_date'))
            args = {
                'nsf_fee': format_currency(email_msg.get('nsfFee')),
                'invoice_total': format_currency(email_msg.get('invoice_total')),
                'invoice_process_date': get_local_formatted_date(invoice_process_date, '%m-%d-%Y')
            }
            logo_url = email_msg.get('logo_url')
            email_dict = common_mailer.process(org_id, admin_coordinator_emails, template_name,
                                               subject, logo_url=logo_url,
                                               **args)
        elif message_type in (MessageType.ONLINE_BANKING_OVER_PAYMENT.value,
                              MessageType.ONLINE_BANKING_UNDER_PAYMENT.value, MessageType.ONLINE_BANKING_PAYMENT.value):

            if message_type == MessageType.ONLINE_BANKING_OVER_PAYMENT.value:
                template_name = TemplateType.ONLINE_BANKING_OVER_PAYMENT_TEMPLATE_NAME.value
            elif message_type == MessageType.ONLINE_BANKING_UNDER_PAYMENT.value:
                template_name = TemplateType.ONLINE_BANKING_UNDER_PAYMENT_TEMPLATE_NAME.value
            else:
                template_name = TemplateType.ONLINE_BANKING_PAYMENT_TEMPLATE_NAME.value

            org_id = email_msg.get('accountId')
            admin_emails = get_member_emails(org_id, (ADMIN,))
            subject = SubjectType.ONLINE_BANKING_PAYMENT_SUBJECT.value
            args = {
                'title': subject,
                'paid_amount': format_currency(email_msg.get('amount')),
                'credit_amount': format_currency(email_msg.get('creditAmount')),
            }
            logo_url = email_msg.get('logo_url')
            email_dict = common_mailer.process(org_id, admin_emails, template_name,
                                               subject, logo_url=logo_url,
                                               **args)
        elif message_type == MessageType.PAD_SETUP_FAILED.value:
            template_name = TemplateType.PAD_SETUP_FAILED_TEMPLATE_NAME.value
            org_id = email_msg.get('accountId')
            admin_coordinator_emails = get_member_emails(org_id, (ADMIN,))
            subject = SubjectType.PAD_SETUP_FAILED.value
            args = {
                'accountId': email_msg.get('accountId'),
            }
            logo_url = email_msg.get('logo_url')
            email_dict = common_mailer.process(org_id, admin_coordinator_emails, template_name,
                                               subject, logo_url=logo_url,
                                               **args)
        elif message_type == MessageType.PAYMENT_PENDING.value:
            template_name = TemplateType.PAYMENT_PENDING_TEMPLATE_NAME.value
            org_id = email_msg.get('accountId')
            admin_coordinator_emails = get_member_emails(org_id, (ADMIN,))
            subject = SubjectType.PAYMENT_PENDING.value
            args = {
                'accountId': email_msg.get('accountId'),
                'cfsAccountId': email_msg.get('cfsAccountId'),
                'transactionAmount': format_currency(email_msg.get('transactionAmount')),
            }
            logo_url = email_msg.get('logo_url')
            email_dict = common_mailer.process(org_id, admin_coordinator_emails, template_name,
                                               subject, logo_url=logo_url,
                                               **args)
        elif message_type == MessageType.EJV_FAILED.value:
            email_dict = ejv_failures.process(email_msg)
        elif message_type == MessageType.RESET_PASSCODE.value:
            template_name = TemplateType.RESET_PASSCODE_TEMPLATE_NAME.value

            subject = SubjectType.RESET_PASSCODE.value
            email_msg.update({
                'header': Constants.RESET_PASSCODE_HEADER.value
            })

            email_dict = common_mailer.process(
                org_id=None,
                recipients=email_msg.get('emailAddresses'),
                template_name=template_name,
                subject=subject, **email_msg)

        elif message_type in {MessageType.AFFILIATION_INVITATION_REQUEST.value,
                              MessageType.AFFILIATION_INVITATION_REQUEST_AUTHORIZATION.value}:
            business_name = email_msg.get('businessName')
            email_dict = common_mailer.process(
                **{
                    'org_id': None,
                    'recipients': email_msg.get('emailAddresses'),
                    'template_name': TemplateType[f'{MessageType(message_type).name}_TEMPLATE_NAME'].value,
                    'subject': SubjectType[MessageType(message_type).name].value.format(business_name=business_name),
                    'logo_url': logo_url,
                    'business_name': business_name,
                    'requesting_account': email_msg.get('fromOrgName'),
                    'account_name': email_msg.get('toOrgName'),
                    'is_authorized': email_msg.get('isAuthorized', None),
                    'additional_message': email_msg.get('additionalMessage', None)
                })
        elif message_type in {MessageType.PRODUCT_APPROVED_NOTIFICATION_DETAILED.value,
                              MessageType.PRODUCT_REJECTED_NOTIFICATION_DETAILED.value}:
            subject_descriptor = email_msg.get('subjectDescriptor')
            subject_type = SubjectType[MessageType(message_type).name].value
            email_dict = common_mailer.process(
                **{
                    'org_id': None,
                    'recipients': email_msg.get('emailAddresses'),
                    'template_name': TemplateType[f'{MessageType(message_type).name}_TEMPLATE_NAME'].value,
                    'subject': subject_type.format(subject_descriptor=subject_descriptor),
                    'logo_url': logo_url,
                    'product_access_descriptor': email_msg.get('productAccessDescriptor'),
                    'category_descriptor': email_msg.get('categoryDescriptor'),
                    'is_reapproved': email_msg.get('isReapproved', None),
                    'product_name': email_msg.get('productName', None),
                    'access_disclaimer': email_msg.get('accessDisclaimer', None),
                    'remarks': email_msg.get('remarks', None),
                    'contact_type': email_msg.get('contactType', None)
                })

        else:
            if any(x for x in MessageType if x.value == message_type):
                title = TitleType[MessageType(message_type).name].value

                subject = SubjectType[MessageType(message_type).name].value\
                    .format(user_first_name=email_msg.get('userFirstName'),
                            user_last_name=email_msg.get('userLastName'),
                            product_name=email_msg.get('productName'),
                            account_name=email_msg.get('orgName'),
                            business_name=email_msg.get('businessName')
                            )
                template_name = TemplateType[f'{MessageType(message_type).name}_TEMPLATE_NAME'].value
            else:
                return

            kwargs = {
                'title': title,
                'user_first_name': email_msg.get('userFirstName'),
                'user_last_name': email_msg.get('userLastName'),
                'context_url': email_msg.get('contextUrl'),
                'role': email_msg.get('role'),
                'label': email_msg.get('label'),
                'product_name': email_msg.get('productName'),
                'remarks': email_msg.get('remarks'),
                'applicationDate': email_msg.get('applicationDate'),
                'business_name': email_msg.get('businessName')
            }

            org_id = email_msg.get('accountId')
            logo_url = email_msg.get('logo_url')
            email_dict = common_mailer.process(
                org_id=org_id,
                recipients=email_msg.get('emailAddresses'),
                template_name=template_name,
                logo_url=logo_url,
                subject=subject, **kwargs)

        if email_dict:
            logger.debug('Extracted email msg Recipient: %s ', email_dict.get('recipients', ''))
            process_email(email_dict, FLASK_APP, token)
        else:
            # TODO probably an unhandled event.handle better
            logger.error('No email content generated')


def process_email(email_dict: dict, flask_app: Flask, token: str):  # pylint: disable=too-many-branches
    """Process the email contained in the message."""
    if not flask_app:
        raise QueueException('Flask App not available.')

    with flask_app.app_context():
        logger.debug('Attempting to process email: %s', email_dict.get('recipients', ''))
        # get type from email
        notification_service.send_email(email_dict, token=token)


async def cb_subscription_handler(msg: nats.aio.client.Msg):
    """Use Callback to process Queue Msg objects."""
    event_message = None
    try:
        logger.info('Received raw message seq:%s, data=  %s', msg.sequence, msg.data.decode())
        event_message = json.loads(msg.data.decode('utf-8'))
        logger.debug('Event Message Received: %s', event_message)
        await process_event(event_message, FLASK_APP)
    except Exception:  # NOQA # pylint: disable=broad-except
        # Catch Exception so that any error is still caught and the message is removed from the queue
        logger.error('Queue Error: %s', json.dumps(event_message), exc_info=True)

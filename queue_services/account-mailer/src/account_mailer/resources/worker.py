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
import json
from datetime import datetime
from http import HTTPStatus

from auth_api.services.gcp_queue import queue
from auth_api.services.gcp_queue.gcp_auth import ensure_authorized_queue_user
from auth_api.services.rest_service import RestService
from auth_api.utils.enums import QueueMessageTypes
from auth_api.utils.roles import ADMIN, COORDINATOR
from flask import Blueprint, current_app, request

from account_mailer.auth_utils import get_login_url, get_member_emails
from account_mailer.email_processors import (
    account_unlock, common_mailer, ejv_failures, pad_confirmation, product_confirmation, refund_requested)
from account_mailer.enums import Constants, SubjectType, TemplateType, TitleType
from account_mailer.services import minio_service, notification_service
from account_mailer.utils import format_currency, format_day_with_suffix, get_local_formatted_date


bp = Blueprint('worker', __name__)


@bp.route('/', methods=('POST',))
@ensure_authorized_queue_user
def worker():
    """Worker to handle incoming queue pushes."""
    if not (event_message := queue.get_simple_cloud_event(request)):
        # Return a 200, so event is removed from the Queue
        return {}, HTTPStatus.OK

    try:
        message_type, email_msg = event_message.type, event_message.data
        current_app.logger.debug('message_type received %s', message_type)
        email_msg['logo_url'] = minio_service.MinioService.get_minio_public_url('bc_logo_for_email.png')

        handle_drawdown_request(message_type, email_msg)
        handle_pad_account_create(message_type, email_msg)
        handle_eft_available_notification(message_type, email_msg)
        handle_nsf_lock_unlock_account(message_type, email_msg)
        handle_account_confirmation_period_over(message_type, email_msg)
        handle_team_actions(message_type, email_msg)
        handle_pad_invoice_created(message_type, email_msg)
        handle_online_banking(message_type, email_msg)
        handle_pad_setup_failed(message_type, email_msg)
        handle_payment_pending(message_type, email_msg)
        handle_ejv_failed(message_type, email_msg)
        handle_reset_passcode(message_type, email_msg)
        handle_affiliation_invitation(message_type, email_msg)
        handle_product_actions(message_type, email_msg)
        handle_statement_notification(message_type, email_msg)
        handle_payment_reminder_or_due(message_type, email_msg)

        # Note if you're extending above, make sure to include the new type in handle_other_messages below.
        handle_other_messages(message_type, email_msg)
    except Exception as e: # NOQA # pylint: disable=broad-except
        current_app.logger.error('Queue Error: %s', json.dumps(event_message), exc_info=True)
        current_app.logger.error(e)
    return {}, HTTPStatus.OK


def handle_drawdown_request(message_type, email_msg):
    """Handle the drawdown request message."""
    if message_type != QueueMessageTypes.REFUND_DRAWDOWN_REQUEST.value:
        return
    email_dict = refund_requested.process(email_msg)
    process_email(email_dict)


def handle_pad_account_create(message_type, email_msg):
    """Handle the pad account create message."""
    if message_type != QueueMessageTypes.PAD_ACCOUNT_CREATE.value:
        return
    email_msg['registry_logo_url'] = minio_service.MinioService.get_minio_public_url('bc_registry_logo_pdf.svg')
    token = RestService.get_service_account_token()
    email_dict = pad_confirmation.process(email_msg, token)
    process_email(email_dict, token)


def handle_eft_available_notification(message_type, email_msg):
    """Handle the eft available notification message."""
    if message_type != QueueMessageTypes.EFT_AVAILABLE_NOTIFICATION.value:
        return
    template_name = TemplateType.EFT_AVAILABLE_NOTIFICATION_TEMPLATE_NAME.value
    org_id = email_msg.get('accountId')
    admin_emails = get_member_emails(org_id, (ADMIN,))
    subject = SubjectType.EFT_AVAILABLE_NOTIFICATION.value
    context_url = f'{get_login_url()}/account/{org_id}/settings/payment-option'
    logo_url = email_msg.get('logo_url')
    email_dict = common_mailer.process(org_id, admin_emails, template_name, subject,
                                       logo_url=logo_url, context_url=context_url)
    process_email(email_dict)


def handle_nsf_lock_unlock_account(message_type, email_msg):
    """Handle the NSF lock/unlock account message."""
    if message_type == QueueMessageTypes.NSF_LOCK_ACCOUNT.value:
        current_app.logger.debug('lock account message recieved:')
        template_name = TemplateType.NSF_LOCK_ACCOUNT_TEMPLATE_NAME.value
        org_id = email_msg.get('accountId')
        admin_coordinator_emails = get_member_emails(org_id, (ADMIN, COORDINATOR))
        subject = SubjectType.NSF_LOCK_ACCOUNT_SUBJECT.value
        logo_url = email_msg.get('logo_url')
        email_dict = common_mailer.process(org_id, admin_coordinator_emails, template_name,
                                           subject, logo_url=logo_url)
        process_email(email_dict)
    elif message_type == QueueMessageTypes.NSF_UNLOCK_ACCOUNT.value:
        current_app.logger.debug('unlock account message received')
        template_name = TemplateType.NSF_UNLOCK_ACCOUNT_TEMPLATE_NAME.value
        org_id = email_msg.get('accountId')
        admin_coordinator_emails = get_member_emails(org_id, (ADMIN, COORDINATOR))
        subject = SubjectType.NSF_UNLOCK_ACCOUNT_SUBJECT.value
        logo_url = email_msg.get('logo_url')

        email_dict = {
            'template_vars': email_msg,
            'logo_url': logo_url,
            'template_name': template_name,
            'subject': subject,
            'org_id': org_id,
            'admin_coordinator_emails': admin_coordinator_emails,
            'account_name': email_msg.get('accountName')
        }

        token = RestService.get_service_account_token()
        email_dict = account_unlock.process(data=email_dict, token=token)
        process_email(email_dict, token)


def handle_account_confirmation_period_over(message_type, email_msg):
    """Handle the account confirmation period over message."""
    if message_type != QueueMessageTypes.ACCOUNT_CONFIRMATION_PERIOD_OVER.value:
        return
    template_name = TemplateType.ACCOUNT_CONF_OVER_TEMPLATE_NAME.value
    org_id = email_msg.get('accountId')
    nsf_fee = format_currency(email_msg.get('nsfFee'))
    admin_coordinator_emails = get_member_emails(org_id, (ADMIN,))
    subject = SubjectType.ACCOUNT_CONF_OVER_SUBJECT.value
    logo_url = email_msg.get('logo_url')
    email_dict = common_mailer.process(org_id, admin_coordinator_emails, template_name, subject,
                                       nsf_fee=nsf_fee, logo_url=logo_url)
    process_email(email_dict)


def handle_team_actions(message_type, email_msg):
    """Handle the team actions messages."""
    if message_type in (QueueMessageTypes.TEAM_MODIFIED.value, QueueMessageTypes.TEAM_MEMBER_INVITED.value):
        current_app.logger.debug('Team Modified message received')
        template_name = TemplateType.TEAM_MODIFIED_TEMPLATE_NAME.value
        org_id = email_msg.get('accountId')
        admin_coordinator_emails = get_member_emails(org_id, (ADMIN,))
        subject = SubjectType.TEAM_MODIFIED_SUBJECT.value
        logo_url = email_msg.get('logo_url')
        email_dict = common_mailer.process(org_id, admin_coordinator_emails, template_name,
                                           subject, logo_url=logo_url)
        process_email(email_dict)
    elif message_type == QueueMessageTypes.ADMIN_REMOVED.value:
        current_app.logger.debug('ADMIN_REMOVED message received')
        template_name = TemplateType.ADMIN_REMOVED_TEMPLATE_NAME.value
        org_id = email_msg.get('accountId')
        recipient_email = email_msg.get('recipientEmail')
        subject = SubjectType.ADMIN_REMOVED_SUBJECT.value
        logo_url = email_msg.get('logo_url')
        email_dict = common_mailer.process(org_id, recipient_email, template_name,
                                           subject, logo_url=logo_url)
        process_email(email_dict)


def handle_pad_invoice_created(message_type, email_msg):
    """Handle the pad invoice created message."""
    if message_type != QueueMessageTypes.PAD_INVOICE_CREATED.value:
        return
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
    process_email(email_dict)


def handle_online_banking(message_type, email_msg):
    """Handle the online banking payment message."""
    if message_type not in (QueueMessageTypes.ONLINE_BANKING_OVER_PAYMENT.value,
                            QueueMessageTypes.ONLINE_BANKING_UNDER_PAYMENT.value,
                            QueueMessageTypes.ONLINE_BANKING_PAYMENT.value):
        return

    if message_type == QueueMessageTypes.ONLINE_BANKING_OVER_PAYMENT.value:
        template_name = TemplateType.ONLINE_BANKING_OVER_PAYMENT_TEMPLATE_NAME.value
    elif message_type == QueueMessageTypes.ONLINE_BANKING_UNDER_PAYMENT.value:
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
    process_email(email_dict)


def handle_pad_setup_failed(message_type, email_msg):
    """Handle the pad setup failed message."""
    if message_type != QueueMessageTypes.PAD_SETUP_FAILED.value:
        return
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
    process_email(email_dict)


def handle_payment_pending(message_type, email_msg):
    """Handle the payment pending message."""
    if message_type != QueueMessageTypes.PAYMENT_PENDING.value:
        return
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
    process_email(email_dict)


def handle_ejv_failed(message_type, email_msg):
    """Handle the ejv failed message."""
    if message_type != QueueMessageTypes.EJV_FAILED.value:
        return
    email_dict = ejv_failures.process(email_msg)
    process_email(email_dict)


def handle_reset_passcode(message_type, email_msg):
    """Handle the reset passcode message."""
    if message_type != QueueMessageTypes.RESET_PASSCODE.value:
        return

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
    process_email(email_dict)


def handle_affiliation_invitation(message_type, email_msg):
    """Handle the affiliation invitation messages."""
    if message_type not in {QueueMessageTypes.AFFILIATION_INVITATION_REQUEST.value,
                            QueueMessageTypes.AFFILIATION_INVITATION_REQUEST_AUTHORIZATION.value}:
        return
    business_name = email_msg.get('businessName')
    logo_url = email_msg.get('logo_url')
    requesting_account = email_msg.get('fromOrgName')
    if from_branch_name := email_msg.get('fromOrgBranchName'):
        requesting_account += ' - ' + from_branch_name

    account = email_msg.get('toOrgName')
    if to_branch_name := email_msg.get('toOrgBranchName'):
        account += ' - ' + to_branch_name

    email_dict = common_mailer.process(
        **{
            'org_id': None,
            'recipients': email_msg.get('emailAddresses'),
            'template_name': TemplateType[f'{QueueMessageTypes(message_type).name}_TEMPLATE_NAME'].value,
            'subject': SubjectType[QueueMessageTypes(message_type).name].value.format(business_name=business_name),
            'logo_url': logo_url,
            'business_name': business_name,
            'requesting_account': requesting_account,
            'account': account,
            'is_authorized': email_msg.get('isAuthorized', None),
            'additional_message': email_msg.get('additionalMessage', None)
        })
    process_email(email_dict)


def handle_product_actions(message_type, email_msg):
    """Handle the product actions messages."""
    if message_type not in {QueueMessageTypes.PRODUCT_APPROVED_NOTIFICATION_DETAILED.value,
                            QueueMessageTypes.PRODUCT_REJECTED_NOTIFICATION_DETAILED.value,
                            QueueMessageTypes.PRODUCT_CONFIRMATION_NOTIFICATION.value}:
        return
    logo_url = email_msg.get('logo_url')
    subject_descriptor = email_msg.get('subjectDescriptor')
    subject_type = SubjectType[QueueMessageTypes(message_type).name].value
    attachment_type = email_msg.get('attachmentType', None)
    email_dict = common_mailer.process(
        **{
            'org_id': None,
            'recipients': email_msg.get('emailAddresses'),
            'template_name': TemplateType[f'{QueueMessageTypes(message_type).name}_TEMPLATE_NAME'].value,
            'subject': subject_type.format(subject_descriptor=subject_descriptor),
            'logo_url': logo_url,
            'product_access_descriptor': email_msg.get('productAccessDescriptor'),
            'category_descriptor': email_msg.get('categoryDescriptor'),
            'is_reapproved': email_msg.get('isReapproved', None),
            'product_name': email_msg.get('productName', None),
            'access_disclaimer': email_msg.get('accessDisclaimer', None),
            'remarks': email_msg.get('remarks', None),
            'contact_type': email_msg.get('contactType', None),
            'has_agreement_attachment': email_msg.get('hasAgreementAttachment', None),
            'attachment_type': attachment_type
        })

    email_dict = product_confirmation.process_attachment(email_dict, attachment_type)
    process_email(email_dict)


def handle_statement_notification(message_type, email_msg):
    """Handle the statement notification message."""
    if message_type not in {QueueMessageTypes.STATEMENT_NOTIFICATION.value}:
        return
    from_date = datetime.fromisoformat(email_msg.get('fromDate'))
    to_date = datetime.fromisoformat(email_msg.get('toDate'))
    logo_url = email_msg.get('logo_url')
    email_dict = common_mailer.process(
        **{
            'org_id': email_msg.get('accountId'),
            'recipients': email_msg.get('emailAddresses'),
            'template_name': TemplateType[f'{QueueMessageTypes(message_type).name}_TEMPLATE_NAME'].value,
            'subject': SubjectType[QueueMessageTypes(message_type).name].value,
            'logo_url': logo_url,
            'from_date': from_date.strftime('%B ') + format_day_with_suffix(from_date.day),
            'to_date': to_date.strftime('%B ') + format_day_with_suffix(to_date.day),
            'total_amount_owing': format_currency(email_msg.get('totalAmountOwing')),
            'statement_frequency': email_msg.get('statementFrequency').lower()
        })
    process_email(email_dict)


def handle_payment_reminder_or_due(message_type, email_msg):
    """Handle the payment reminder or due message."""
    if message_type not in {QueueMessageTypes.PAYMENT_REMINDER_NOTIFICATION.value,
                            QueueMessageTypes.PAYMENT_DUE_NOTIFICATION.value}:
        return
    due_date = datetime.fromisoformat(email_msg.get('dueDate'))
    logo_url = email_msg.get('logo_url')
    email_dict = common_mailer.process(
        **{
            'org_id': email_msg.get('accountId'),
            'recipients': email_msg.get('emailAddresses'),
            'template_name': TemplateType[f'{QueueMessageTypes(message_type).name}_TEMPLATE_NAME'].value,
            'subject': SubjectType[QueueMessageTypes(message_type).name].value,
            'logo_url': logo_url,
            'due_date': due_date.strftime('%B ') + format_day_with_suffix(due_date.day) + f' {due_date.year}',
            'total_amount_owing': format_currency(email_msg.get('totalAmountOwing')),
            'statement_frequency': email_msg.get('statementFrequency').lower()
        })
    process_email(email_dict)


def handle_other_messages(message_type, email_msg):
    """Handle the other messages not in the list."""
    if message_type in [
        QueueMessageTypes.REFUND_DRAWDOWN_REQUEST.value,
        QueueMessageTypes.PAD_ACCOUNT_CREATE.value,
        QueueMessageTypes.EFT_AVAILABLE_NOTIFICATION.value,
        QueueMessageTypes.NSF_LOCK_ACCOUNT.value,
        QueueMessageTypes.NSF_UNLOCK_ACCOUNT.value,
        QueueMessageTypes.TEAM_MODIFIED.value,
        QueueMessageTypes.TEAM_MEMBER_INVITED.value,
        QueueMessageTypes.ADMIN_REMOVED.value,
        QueueMessageTypes.ACCOUNT_CONFIRMATION_PERIOD_OVER.value,
        QueueMessageTypes.PAD_INVOICE_CREATED.value,
        QueueMessageTypes.ONLINE_BANKING_OVER_PAYMENT.value,
        QueueMessageTypes.ONLINE_BANKING_UNDER_PAYMENT.value,
        QueueMessageTypes.ONLINE_BANKING_PAYMENT.value,
        QueueMessageTypes.PAD_SETUP_FAILED.value,
        QueueMessageTypes.PAYMENT_PENDING.value,
        QueueMessageTypes.EJV_FAILED.value,
        QueueMessageTypes.RESET_PASSCODE.value,
        QueueMessageTypes.AFFILIATION_INVITATION_REQUEST.value,
        QueueMessageTypes.AFFILIATION_INVITATION_REQUEST_AUTHORIZATION.value,
        QueueMessageTypes.PRODUCT_APPROVED_NOTIFICATION_DETAILED.value,
        QueueMessageTypes.PRODUCT_REJECTED_NOTIFICATION_DETAILED.value,
        QueueMessageTypes.PRODUCT_CONFIRMATION_NOTIFICATION.value,
        QueueMessageTypes.STATEMENT_NOTIFICATION.value,
        QueueMessageTypes.PAYMENT_REMINDER_NOTIFICATION.value,
        QueueMessageTypes.PAYMENT_DUE_NOTIFICATION.value
    ]:
        return

    if any(x for x in QueueMessageTypes if x.value == message_type):
        title = TitleType[QueueMessageTypes(message_type).name].value

        subject = SubjectType[QueueMessageTypes(message_type).name].value\
            .format(user_first_name=email_msg.get('userFirstName'),
                    user_last_name=email_msg.get('userLastName'),
                    product_name=email_msg.get('productName'),
                    account_name=email_msg.get('orgName'),
                    business_name=email_msg.get('businessName')
                    )
        template_name = TemplateType[f'{QueueMessageTypes(message_type).name}_TEMPLATE_NAME'].value
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
    process_email(email_dict)


def process_email(email_dict: dict, token: str = None):  # pylint: disable=too-many-branches
    """Process the email contained in the message."""
    current_app.logger.debug('Attempting to process email: %s', email_dict.get('recipients', ''))
    if email_dict:
        if not token:
            token = RestService.get_service_account_token()
        notification_service.send_email(email_dict, token=token)
    else:
        current_app.logger.error('No email content generated')

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
"""Test Suite to ensure the worker routines are working as expected."""
from datetime import datetime
from unittest.mock import patch

import pytest
from entity_queue_common.service_utils import subscribe_to_queue

from account_mailer.enums import MessageType, SubjectType
from account_mailer.services import notification_service
from account_mailer.services.minio_service import MinioService
from account_mailer.utils import get_local_formatted_date

from . import factory_membership_model, factory_org_model, factory_user_model_with_contact
from .utils import helper_add_event_to_queue, helper_add_ref_req_to_queue


@pytest.mark.asyncio
async def test_account_mailer_queue(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    # vars
    org_id = '1'

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'

    # Create a Credit Card Payment

    # register the handler to test it
    await subscribe_to_queue(events_stan,
                             events_subject,
                             events_queue,
                             events_durable_name,
                             cb_subscription_handler)

    # add an event to queue
    mail_details = {
        'type': 'payment_completed'
    }
    await helper_add_event_to_queue(events_stan, events_subject, org_id=org_id, mail_details=mail_details)

    assert True


@pytest.mark.asyncio
async def test_refund_request(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that the refund request event works."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    # vars
    invoice_id = '1'
    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'

    # register the handler to test it
    await subscribe_to_queue(events_stan,
                             events_subject,
                             events_queue,
                             events_durable_name,
                             cb_subscription_handler)

    # add an event to queue
    mail_details = {
        'identifier': 'NR 123456789',
        'orderNumber': '1',
        'transactionDateTime': '2020-12-12 14:10:20',
        'transactionAmount': 50.00,
        'transactionId': 'REG1234'
    }
    await helper_add_ref_req_to_queue(events_stan, events_subject, invoice_id=invoice_id, mail_details=mail_details)

    assert True  # If no errors, we assumed test passed.

    # Test drawdown refund
    mail_details = {
        'identifier': 'NR 123456789',
        'orderNumber': '1',
        'transactionDateTime': '2020-12-12 14:10:20',
        'transactionAmount': 50.00,
        'transactionId': 'REG1234',
        'refunDate': '2000-01-01',
        'bcolAccount': '12345',
        'bcolUser': '009900'
    }
    await helper_add_ref_req_to_queue(events_stan, events_subject, invoice_id=invoice_id, mail_details=mail_details,
                                      pay_method='drawdown')


@pytest.mark.asyncio
async def test_lock_account_mailer_queue(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    # vars
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'
    with patch.object(notification_service, 'send_email', return_value=None) as mock_send:
        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                 events_subject,
                                 events_queue,
                                 events_durable_name,
                                 cb_subscription_handler)

        # add an event to queue
        mail_details = {
            'accountId': id,
            'accountName': org.name
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.NSF_LOCK_ACCOUNT.value, mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'foo@bar.com'
        assert mock_send.call_args.args[0].get('content').get('subject') == SubjectType.NSF_LOCK_ACCOUNT_SUBJECT.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert True


@pytest.mark.asyncio
async def test_unlock_account_mailer_queue(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    # vars
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'
    with patch.object(notification_service, 'send_email', return_value=None) as mock_send:
        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                 events_subject,
                                 events_queue,
                                 events_durable_name,
                                 cb_subscription_handler)

        # add an event to queue
        mail_details = {
            'accountId': id,
            'accountName': org.name
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.NSF_UNLOCK_ACCOUNT.value, mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'foo@bar.com'
        assert mock_send.call_args.args[0].get('content').get('subject') == SubjectType.NSF_UNLOCK_ACCOUNT_SUBJECT.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert mock_send.call_args.args[0].get('content').get('body') is not None
        assert True


@pytest.mark.asyncio
async def test_account_conf_mailer_queue(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    # vars
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'
    with patch.object(notification_service, 'send_email', return_value=None) as mock_send:
        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                 events_subject,
                                 events_queue,
                                 events_durable_name,
                                 cb_subscription_handler)

        # add an event to queue
        mail_details = {
            'accountId': id,
            'nsfFee': '30'
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.ACCOUNT_CONFIRMATION_PERIOD_OVER.value,
                                        mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'foo@bar.com'
        assert mock_send.call_args.args[0].get('content').get('subject') == SubjectType.ACCOUNT_CONF_OVER_SUBJECT.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert mock_send.call_args.args[0].get('content').get('body') is not None


@pytest.mark.asyncio
async def test_account_pad_invoice_mailer_queue(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    # vars
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'
    with patch.object(notification_service, 'send_email', return_value=None) as mock_send:
        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                 events_subject,
                                 events_queue,
                                 events_durable_name,
                                 cb_subscription_handler)

        # add an event to queue, these are provided by cfs_create_invoice_task.
        mail_details = {
            'accountId': id,
            'nsfFee': '30',
            'invoice_total': '100',
            'invoice_process_date': f'{datetime.now()}'
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.PAD_INVOICE_CREATED.value, mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'foo@bar.com'
        assert mock_send.call_args.args[0].get('content').get('subject') == SubjectType.PAD_INVOICE_CREATED.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert mock_send.call_args.args[0].get('content').get('body') is not None
        assert f'hours on {get_local_formatted_date(datetime.now(), "%m-%d-%Y")}' \
            in mock_send.call_args.args[0].get('content').get('body')


@pytest.mark.asyncio
async def test_account_admin_removed(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    # vars
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'
    with patch.object(notification_service, 'send_email', return_value=None) as mock_send:
        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                 events_subject,
                                 events_queue,
                                 events_durable_name,
                                 cb_subscription_handler)

        # add an event to queue
        email = 'foo@testbar.com'
        mail_details = {
            'accountId': id,
            'recipientEmail': email
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.ADMIN_REMOVED.value, mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == email
        assert mock_send.call_args.args[0].get('content').get('subject') == SubjectType.ADMIN_REMOVED_SUBJECT.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert mock_send.call_args.args[0].get('content').get('body') is not None


@pytest.mark.asyncio
async def test_account_team_modified(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    # vars
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'
    with patch.object(notification_service, 'send_email', return_value=None) as mock_send:
        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                 events_subject,
                                 events_queue,
                                 events_durable_name,
                                 cb_subscription_handler)

        # add an event to queue
        mail_details = {
            'accountId': id,
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.TEAM_MEMBER_INVITED.value, mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'foo@bar.com'
        assert mock_send.call_args.args[0].get('content').get('subject') == SubjectType.TEAM_MODIFIED_SUBJECT.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert mock_send.call_args.args[0].get('content').get('body') is not None


@pytest.mark.asyncio
async def test_online_banking_emails(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    # vars
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'
    with patch.object(notification_service, 'send_email', return_value=None) as mock_send:
        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                 events_subject,
                                 events_queue,
                                 events_durable_name,
                                 cb_subscription_handler)

        # add an event to queue
        mail_details = {
            'amount': '100.00',
            'creditAmount': '10.00',
            'accountId': id
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.ONLINE_BANKING_UNDER_PAYMENT.value,
                                        mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'foo@bar.com'
        assert mock_send.call_args.args[0].get('content').get(
            'subject') == SubjectType.ONLINE_BANKING_PAYMENT_SUBJECT.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert mock_send.call_args.args[0].get('content').get('body') is not None

        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.ONLINE_BANKING_OVER_PAYMENT.value,
                                        mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'foo@bar.com'
        assert mock_send.call_args.args[0].get('content').get(
            'subject') == SubjectType.ONLINE_BANKING_PAYMENT_SUBJECT.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert mock_send.call_args.args[0].get('content').get('body') is not None

        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.ONLINE_BANKING_PAYMENT.value,
                                        mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'foo@bar.com'
        assert mock_send.call_args.args[0].get('content').get(
            'subject') == SubjectType.ONLINE_BANKING_PAYMENT_SUBJECT.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert mock_send.call_args.args[0].get('content').get('body') is not None


@pytest.mark.asyncio
async def test_pad_failed_emails(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    # vars
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'
    with patch.object(notification_service, 'send_email', return_value=None) as mock_send:
        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                 events_subject,
                                 events_queue,
                                 events_durable_name,
                                 cb_subscription_handler)

        # add an event to queue
        mail_details = {
            'accountId': id
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.PAD_SETUP_FAILED.value,
                                        mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'foo@bar.com'
        assert mock_send.call_args.args[0].get('content').get(
            'subject') == SubjectType.PAD_SETUP_FAILED.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert mock_send.call_args.args[0].get('content').get('body') is not None

        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.PAD_SETUP_FAILED.value,
                                        mail_details=mail_details)


@pytest.mark.asyncio
async def test_payment_pending_emails(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    # vars
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'
    with patch.object(notification_service, 'send_email', return_value=None) as mock_send:
        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                 events_subject,
                                 events_queue,
                                 events_durable_name,
                                 cb_subscription_handler)

        # add an event to queue
        mail_details = {
            'accountId': id,
            'cfsAccountId': '12345678',
            'transactionAmount': 20.00
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.PAYMENT_PENDING.value,
                                        mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'foo@bar.com'
        assert mock_send.call_args.args[0].get('content').get(
            'subject') == SubjectType.PAYMENT_PENDING.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert mock_send.call_args.args[0].get('content').get('body') is not None

        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.PAYMENT_PENDING.value,
                                        mail_details=mail_details)


@pytest.mark.asyncio
async def test_ejv_failure_emails(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'
    with patch.object(notification_service, 'send_email', return_value=None) as mock_send:
        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                 events_subject,
                                 events_queue,
                                 events_durable_name,
                                 cb_subscription_handler)

        minio_file_name = 'FEEDBACK.1234567890'
        minio_bucket = 'cgi-ejv'

        with open(minio_file_name, 'a+') as jv_file:
            jv_file.write('TEST')
            jv_file.close()

        # Now upload the ACK file to minio and publish message.
        with open(minio_file_name, 'rb') as f:
            MinioService.put_minio_file(minio_bucket, minio_file_name, f.read())

        # add an event to queue
        mail_details = {
            'fileName': minio_file_name,
            'minioLocation': minio_bucket
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.EJV_FAILED.value,
                                        mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'test@test.com'
        assert mock_send.call_args.args[0].get('content').get('subject') == SubjectType.EJV_FAILED.value


@pytest.mark.asyncio
async def test_passcode_reset_email(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from account_mailer.worker import cb_subscription_handler

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'
    with patch.object(notification_service, 'send_email', return_value=None) as mock_send:
        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                 events_subject,
                                 events_queue,
                                 events_durable_name,
                                 cb_subscription_handler)

        # add an event to queue - staff initiated reset
        msg_payload = {
            'emailAddresses': 'test@test.com',
            'passCode': '1234',
            'businessIdentifier': 'CP1234',
            'businessName': 'TEST',
            'isStaffInitiated': True
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.RESET_PASSCODE.value,
                                        mail_details=msg_payload)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'test@test.com'
        assert mock_send.call_args.args[0].get('content').get('subject') == SubjectType.RESET_PASSCODE.value

        # add an event to queue - staff initiated reset
        msg_payload = {
            'emailAddresses': 'test@test.com',
            'passCode': '1234',
            'businessIdentifier': 'CP1234',
            'businessName': 'TEST',
            'isStaffInitiated': False
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.RESET_PASSCODE.value,
                                        mail_details=msg_payload)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'test@test.com'
        assert mock_send.call_args.args[0].get('content').get('subject') == SubjectType.RESET_PASSCODE.value

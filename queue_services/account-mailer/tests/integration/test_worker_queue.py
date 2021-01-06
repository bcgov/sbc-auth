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
from unittest.mock import patch

import pytest
from entity_queue_common.service_utils import subscribe_to_queue

from account_mailer.enums import MessageType, SubjectType
from account_mailer.services import notification_service

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

        # add an event to queue
        mail_details = {
            'accountId': id,
            'nsfFee': '30',
            'invoice_total': '100'
        }
        await helper_add_event_to_queue(events_stan, events_subject, org_id=id,
                                        msg_type=MessageType.PAD_INVOICE_CREATED.value, mail_details=mail_details)

        mock_send.assert_called
        assert mock_send.call_args.args[0].get('recipients') == 'foo@bar.com'
        assert mock_send.call_args.args[0].get('content').get('subject') == SubjectType.PAD_INVOICE_CREATED.value
        assert mock_send.call_args.args[0].get('attachments') is None
        assert mock_send.call_args.args[0].get('content').get('body') is not None


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

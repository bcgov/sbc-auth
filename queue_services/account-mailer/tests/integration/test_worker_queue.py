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

import pytest
from entity_queue_common.service_utils import subscribe_to_queue

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

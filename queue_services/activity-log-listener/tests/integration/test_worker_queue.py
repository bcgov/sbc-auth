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

from .utils import helper_add_event_to_queue


@pytest.mark.asyncio
async def test_events_listener_queue(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from activity_log_listener.worker import cb_subscription_handler

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'

    # register the handler to test it
    await subscribe_to_queue(events_stan,
                             events_subject,
                             events_queue,
                             events_durable_name,
                             cb_subscription_handler)
    event_details = {
        'action': 'test_action',
        'itemType': 'test_type',
        'itemName': 'test_name',
        'itemId': '100',
        'actor': 'test_Actor',
        'remoteAddr': ''
    }

    # add an event to queue
    await helper_add_event_to_queue(events_stan, events_subject, event_details=event_details)

    assert True

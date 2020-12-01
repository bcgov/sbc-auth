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
from auth_api.models import Org as OrgModel
from entity_queue_common.service_utils import subscribe_to_queue

from tests.integration import factory_org_model

from .utils import helper_add_event_to_queue


@pytest.mark.asyncio
async def test_events_listener_queue(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from events_listener.worker import cb_subscription_handler

    # vars
    org_id = '1'
    status = 'lock'

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
    await helper_add_event_to_queue(events_stan, events_subject, org_id=org_id,
                                    action=status)

    assert True


@pytest.mark.asyncio
async def test_update_internal_payment(app, session, stan_server, event_loop, client_id, events_stan, future):
    """Assert that the update internal payment records works."""
    # Call back for the subscription
    from events_listener.worker import cb_subscription_handler

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'

    org = factory_org_model()
    id = org.id
    # register the handler to test it
    await subscribe_to_queue(events_stan,
                             events_subject,
                             events_queue,
                             events_durable_name,
                             cb_subscription_handler)

    # add an event to queue
    await helper_add_event_to_queue(events_stan, events_subject, org_id=org.id,
                                    action='lock')

    # Get the internal account and invoice and assert that the identifier is new identifier
    new_org = OrgModel.find_by_org_id(id)
    assert new_org.status_code == 'NSF_SUSPENDED'

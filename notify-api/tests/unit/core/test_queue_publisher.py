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

"""Tests to assure the Queue integration layer.

Test-Suite to ensure that the Queue publishing is working as expected.
"""
import json

import pytest

from notify_api.core.queue_publisher import subscribe_to_queue


@pytest.mark.asyncio
async def test_publish(app, stan_server, client_id, stan, future, event_loop):
    """Assert that payment tokens can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    async def subscriber_callback(msg):
        message_dict = json.loads(msg.data.decode('utf-8'))
        assert 'notificationId' in message_dict

    await subscribe_to_queue(stan, subscriber_callback)

    # publish message
    from notify_api.core.queue_publisher import publish

    payload = {'notificationId': 1}

    await publish(payload=payload)

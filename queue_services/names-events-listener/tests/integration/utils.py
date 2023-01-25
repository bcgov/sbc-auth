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
"""Utilities used by the integration tests."""
import json
from datetime import datetime
from random import randint

import stan


async def helper_add_event_to_queue(stan_client: stan.aio.client.Client,
                                    subject: str,
                                    nr_number: str,
                                    new_state: str,
                                    old_state: str):
    """Add event to the Queue."""
    payload = {
        'specversion': '1.0.1',
        'type': 'bc.registry.names.events',
        'source': '/requests/6724165',
        'id': 1234,
        'time': str(datetime.now()),
        'datacontenttype': 'application/json',
        'identifier': '781020202',
        'data': {
            'request': {
                'nrNum': nr_number,
                'newState': new_state,
                'previousState': old_state
            }
        }
    }

    await stan_client.publish(subject=subject,
                              payload=json.dumps(payload).encode('utf-8'))


def get_random_number():
    """Generate a random and return."""
    return randint(100000000, 999999999)

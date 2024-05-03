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
"""Utilities used by the unit tests."""
import base64
import json
import uuid
from datetime import datetime, timezone
from random import randint

from sbc_common_components.utils.enums import QueueMessageTypes
from simple_cloudevent import SimpleCloudEvent, to_queue_message


def build_request_for_queue_push(message_type, payload):
    """Build request for queue message."""
    queue_message_bytes = to_queue_message(SimpleCloudEvent(
        id=str(uuid.uuid4()),
        source='pay-queue',
        subject=None,
        time=datetime.now(tz=timezone.utc).isoformat(),
        type=message_type,
        data=payload
    ))

    return {
        'message': {
            'data': base64.b64encode(queue_message_bytes).decode('utf-8')
        },
        'subscription': 'foobar'
    }


def post_to_queue(client, request_payload):
    """Post request to worker using an http request on our wrapped flask instance."""
    response = client.post('/', data=json.dumps(request_payload),
                           headers={'Content-Type': 'application/json'})
    assert response.status_code == 200


def helper_add_activity_log_event_to_queue(client, details):
    """Add event to the Queue."""
    payload = build_request_for_queue_push(QueueMessageTypes.ACTIVITY_LOG.value, details)
    post_to_queue(client, payload)


def helper_add_lock_unlock_event_to_queue(client, message_type: str, org_id):
    """Add event to the Queue."""
    queue_payload = {
        'accountId': org_id,
        'accountName': 'DEV - PAD01'
    }
    payload = build_request_for_queue_push(message_type, queue_payload)
    post_to_queue(client, payload)


def helper_add_nr_event_to_queue(client,
                                 nr_number: str,
                                 new_state: str,
                                 old_state: str):
    """Add event to the Queue."""
    queue_payload = {
        'request': {
            'nrNum': nr_number,
            'newState': new_state,
            'previousState': old_state
        }
    }
    payload = build_request_for_queue_push(QueueMessageTypes.NAMES_EVENT.value, queue_payload)
    post_to_queue(client, payload)


def get_random_number():
    """Generate a random and return."""
    return randint(100000000, 999999999)

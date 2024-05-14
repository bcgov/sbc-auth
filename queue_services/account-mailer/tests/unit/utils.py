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
"""Utilities used by the unit tests."""
import base64
import json
import uuid
from datetime import datetime, timezone

from simple_cloudevent import SimpleCloudEvent, to_queue_message


def build_request_for_queue_push(message_type, payload):
    """Build request for queue message."""
    queue_message_bytes = to_queue_message(SimpleCloudEvent(
        id=str(uuid.uuid4()),
        source='account-mailer',
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


def helper_add_event_to_queue(client, message_type: str, mail_details: dict):
    """Add event to the Queue."""
    if not mail_details:
        mail_details = {
        }
    payload = build_request_for_queue_push(message_type, mail_details)
    post_to_queue(client, payload)

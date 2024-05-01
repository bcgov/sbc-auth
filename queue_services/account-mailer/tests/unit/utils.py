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
import json
import uuid
from datetime import datetime, timezone



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

def helper_add_event_to_queue(subject: str,
                                    org_id: str = '1', msg_type='account.mailer', mail_details: dict = {}):
    """Add event to the Queue."""
    queue_payload = {
        'fileName': file_name,
        'location': current_app.config['MINIO_BUCKET_NAME']
    }
    payload = build_request_for_queue_push(message_type, queue_payload)
    post_to_queue(client, payload)


    payload = {
        'specversion': '1.x-wip',
        'type': msg_type,
        'source': f'https://api.pay.bcregistry.gov.bc.ca/v1/accounts/{org_id}',
        'id': f'{org_id}',
        'time': '2020-08-28T17:37:34.651294+00:00',
        'datacontenttype': 'application/json',
        'data': mail_details
    }
    # TODO publish
    #await stan_client.publish(subject=subject,
                              #payload=json.dumps(payload).encode('utf-8'))


def helper_add_ref_req_to_queue(
                                      subject: str,
                                      invoice_id: str = '1', mail_details: dict = {},
                                      pay_method: str = 'direct_pay'):
    """Add a refund request event to the Queue."""
    payload = {
        'specversion': '1.x-wip',
        'type': f'bc.registry.payment.{pay_method}.refundRequest',
        'source': f'https://api.pay.bcregistry.gov.bc.ca/v1/invoices/{invoice_id}',
        'id': f'{invoice_id}',
        'time': '2020-08-28T17:37:34.651294+00:00',
        'datacontenttype': 'application/json',
        'data': mail_details
    }
    # TODO publish

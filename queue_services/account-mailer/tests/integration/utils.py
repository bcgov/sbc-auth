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

import stan


async def helper_add_event_to_queue(stan_client: stan.aio.client.Client,
                                    subject: str,
                                    org_id: str = '1', mail_details: dict = {}):
    """Add event to the Queue."""
    payload = {
        'specversion': '1.x-wip',
        'type': 'account.mailer',
        'source': f'https://api.pay.bcregistry.gov.bc.ca/v1/accounts/{org_id}',
        'id': f'{org_id}',
        'time': '2020-08-28T17:37:34.651294+00:00',
        'datacontenttype': 'application/json',
        'data': mail_details
    }
    await stan_client.publish(subject=subject,
                              payload=json.dumps(payload).encode('utf-8'))


async def helper_add_ref_req_to_queue(stan_client: stan.aio.client.Client,
                                      subject: str,
                                      invoice_id: str = '1', mail_details: dict = {}):
    """Add a refund request event to the Queue."""
    payload = {
        'specversion': '1.x-wip',
        'type': 'bc.registry.payment.refundRequest',
        'source': f'https://api.pay.bcregistry.gov.bc.ca/v1/invoices/{invoice_id}',
        'id': f'{invoice_id}',
        'time': '2020-08-28T17:37:34.651294+00:00',
        'datacontenttype': 'application/json',
        'data': mail_details
    }
    await stan_client.publish(subject=subject,
                              payload=json.dumps(payload).encode('utf-8'))

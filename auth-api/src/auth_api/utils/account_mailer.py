# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""helper to publish to mailer  ."""
from datetime import datetime

from auth_api.config import get_named_config
from auth_api.services.queue_publisher import publish_response


CONFIG = get_named_config()


def publish_to_mailer(notification_type, org_id: str = None, data=None, business_identifier: str = None):
    """Publish from auth to mailer."""
    if data is None:
        data = {
            'accountId': org_id,
        }
    source: str = None
    if org_id:
        source = f'https://api.auth.bcregistry.gov.bc.ca/v1/accounts/{org_id}'
    elif business_identifier:
        source = f'https://api.auth.bcregistry.gov.bc.ca/v1/entities/{business_identifier}'

    payload = {
        'specversion': '1.x-wip',
        'type': f'bc.registry.auth.{notification_type}',
        'source': source,
        'id': org_id,
        'time': f'{datetime.now()}',
        'datacontenttype': 'application/json',
        'data': data
    }
    publish_response(payload=payload, client_name=CONFIG.NATS_MAILER_CLIENT_NAME,
                     subject=CONFIG.NATS_MAILER_SUBJECT)

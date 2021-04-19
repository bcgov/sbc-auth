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
"""Service for publishing the activity stream data."""
import json
import uuid
from datetime import datetime

from flask import current_app, g
from sqlalchemy_continuum.plugins.flask import fetch_remote_addr

from auth_api.config import get_named_config
from auth_api.services.queue_publisher import publish_response

CONFIG = get_named_config()


def publish_activity(action: str, item_type: str, item_name: str, item_id: str):  # pylint:disable=unused-argument
    """Publish the activity asynchronously, using the given details."""

    data = {
        'action': action,
        'item_type': item_type,
        'item_name': item_name,
        'item_id': item_id,
        'actor': g.jwt_oidc_token_info.get('preferred_username',
                                           None) if g and 'jwt_oidc_token_info' in g else None,
        'remote_addr': fetch_remote_addr()

    }
    source = f'https://api.auth.bcregistry.gov.bc.ca/v1/accounts'

    payload = {
        'specversion': '1.x-wip',
        'type': f'bc.registry.auth.activity',
        'source': source,
        'id': uuid.uuid1(),
        'time': f'{datetime.now()}',
        'datacontenttype': 'application/json',
        'data': data
    }
    publish_response(payload=payload, client_name=CONFIG.NATS_MAILER_CLIENT_NAME,
                     subject=CONFIG.NATS_MAILER_SUBJECT)

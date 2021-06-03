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
import uuid
from datetime import datetime

from flask import current_app, g
from sentry_sdk import capture_message
from sqlalchemy_continuum.plugins.flask import fetch_remote_addr

from auth_api.config import get_named_config
from auth_api.models import User as UserModel
from auth_api.services.queue_publisher import publish_response

CONFIG = get_named_config()


def publish_activity(action: str, item_name: str,
                     item_id: str, org_id: int = None, user_id=None, **kwargs):  # pylint:disable=unused-argument
    """Publish the activity asynchronously, using the given details."""
    try:
        # find user_id if haven't passed in
        if not user_id and g and 'jwt_oidc_token_info' in g:
            user: UserModel = UserModel.find_by_jwt_token()
            user_id = user.id

        data = {
            'action': action,
            'itemType': 'ACCOUNT',
            'itemName': item_name,
            'itemId': item_id,
            'orgId': org_id,
            'actor': user_id,
            'remoteAddr': fetch_remote_addr(),
            'createdAt': f'{datetime.now()}'

        }
        source = 'https://api.auth.bcregistry.gov.bc.ca/v1/accounts'

        payload = {
            'specversion': '1.x-wip',
            'type': 'bc.registry.auth.activity',
            'source': source,
            'id': str(uuid.uuid1()),
            'time': f'{datetime.now()}',
            'datacontenttype': 'application/json',
            'data': data
        }
        publish_response(payload=payload, client_name=CONFIG.NATS_ACTIVITY_CLIENT_NAME,
                         subject=CONFIG.NATS_ACTIVITY_SUBJECT)
    except Exception as err:  # noqa: B902 # pylint: disable=broad-except
        capture_message('Activity Queue Publish Event Error:' + str(err), level='error')
        current_app.logger.error('Activity Queue Publish Event Error:', exc_info=True)

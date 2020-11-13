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
"""Service for managing Invitation data."""
import json

from auth_api.services.rest_service import RestService
from flask import current_app


def send_email(notify_body: dict):  # pylint:disable=unused-argument
    """Send the email asynchronously, using the given details."""
    current_app.logger.info(f'send_email to {notify_body.get("recipients")}')
    notify_url = current_app.config.get('NOTIFY_API_URL') + '/notify/'

    notify_response = RestService.post(notify_url, data=notify_body)
    current_app.logger.info('send_email notify_response')
    if notify_response:
        response_json = json.loads(notify_response.text)
        if response_json['notifyStatus']['code'] != 'FAILURE':
            return True

    return False

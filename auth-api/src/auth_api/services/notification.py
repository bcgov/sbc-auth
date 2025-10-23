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

from flask import current_app

from .rest_service import RestService


def send_email(subject: str, recipients: str, html_body: str):
    """Send the email asynchronously, using the given details."""
    current_app.logger.info(f"send_email {recipients}")
    notify_url = current_app.config.get("NOTIFY_API_URL") + "/notify/"
    notify_body = {"recipients": recipients, "content": {"subject": subject, "body": html_body}}

    notify_response = RestService.post(notify_url, data=notify_body)
    current_app.logger.info("send_email notify_response")
    if notify_response:
        response_json = json.loads(notify_response.text)
        if response_json["notifyStatus"]["code"] != "FAILURE":
            return True

    return False

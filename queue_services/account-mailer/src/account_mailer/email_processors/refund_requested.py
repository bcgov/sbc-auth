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
"""Process an email for a refund request."""


from flask import current_app
from jinja2 import Template

from entity_queue_common.service_utils import logger
from account_mailer.email_processors import generate_template


def process(email_msg: dict) -> dict:
    """Build the email for Payment Completed notification."""
    logger.debug('refund_request notification: %s', email_msg)

    # fill in template
    filled_template = generate_template(current_app.config.get("TEMPLATE_PATH"), "refund_request_email")

    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    html_out = jnja_template.render(
        refund_data=email_msg
    )
    return {
        'recipients': current_app.config.get('REFUND_REQUEST').recipients,
        'content': {
            'subject': f'Refund Request for {email_msg.get("identifier")}',
            'body': html_out,
            'attachments': []
        }
    }

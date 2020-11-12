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
from pathlib import Path

from entity_queue_common.service_utils import logger
from flask import current_app
from jinja2 import Template

from account_mailer.email_processors import substitute_template_parts


def process(email_msg: dict) -> dict:
    """Build the email for Payment Completed notification."""
    logger.debug('refund_request notification: %s', email_msg)

    # fill in template
    template = Path(f'{current_app.config.get("TEMPLATE_PATH")}/REFUND_REQUEST.html').read_text()
    filled_template = substitute_template_parts(template)

    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    html_out = jnja_template.render(
        request=email_msg
    )
    return {
        'recipients': current_app.config.get('REFUND_REQUEST').recipients,
        'content': {
            'subject': f'{email_msg.identifier} - Refund Requested',
            'body': html_out,
            'attachments': []
        }
    }

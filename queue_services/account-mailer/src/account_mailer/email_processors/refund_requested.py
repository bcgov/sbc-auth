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

from datetime import datetime

from flask import current_app
from jinja2 import Template

from account_mailer.email_processors import generate_template


def process(event_message: dict) -> dict:
    """Build the email for Payment Completed notification."""
    current_app.logger.debug('refund_request notification: %s', event_message)
    email_msg = event_message.get('data')
    template_name = 'bcol_refund_request_email'
    recepients = current_app.config.get('REFUND_REQUEST').get('bcol').get('recipients')
    refund_date = datetime.strptime(email_msg.get('refundDate'), '%Y%m%d').strftime('%Y-%m-%d')
    subject = f'BC Registries and Online Services Refunds for {refund_date}'

    # fill in template
    filled_template = generate_template(current_app.config.get('TEMPLATE_PATH'), template_name)

    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    html_out = jnja_template.render(
        refund_data=email_msg,
        logo_url=email_msg.get('logo_url')
    )
    return {
        'recipients': recepients,
        'content': {
            'subject': subject,
            'body': html_out,
            'attachments': []
        }
    }

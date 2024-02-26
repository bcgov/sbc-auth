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
"""A Template for the Account Unlocked Email."""

import base64
import datetime

from auth_api.services.rest_service import RestService
from auth_api.utils.enums import AuthHeaderType, ContentType
from entity_queue_common.service_utils import logger
from flask import current_app
from jinja2 import Template

from account_mailer.email_processors import generate_template


def process(data: dict, token: str) -> dict:
    """Build the email for Account Unlocked notification."""
    logger.debug('email_msg notification: %s', data)
    pdf_attachment = _get_account_unlock_pdf(data, token)
    html_body = _get_account_unlock_email(data)
    return {
        'recipients': data.get('admin_coordinator_emails'),
        'content': {
            'subject': data.get('subject'),
            'body': f'{html_body}',
            'attachments': [
                {
                    'fileName': 'Account_Unlock_Receipt.pdf',
                    'fileBytes': pdf_attachment.decode('utf-8'),
                    'fileUrl': '',
                    'attachOrder': '1'
                }
            ]
        }
    }


def _get_account_unlock_email(email_msg):
    filled_template = generate_template(current_app.config.get('TEMPLATE_PATH'), email_msg.get('template_name'))
    jnja_template = Template(filled_template, autoescape=True)
    html_out = jnja_template.render(
        account_name=email_msg.get('accountName'),
        logo_url=email_msg.get('logo_url')
    )
    return html_out


def _get_account_unlock_pdf(data, token):
    current_time = datetime.datetime.now()
    pdf_payload = {
        'reportName': 'NSF_Fee_Receipt',
        'templateVars': data['template_vars'],
        'populatePageNumber': True,
        'templateName': 'payment_receipt',
    }

    report_response = RestService.post(endpoint=current_app.config.get('REPORT_API_BASE_URL'),
                                       token=token,
                                       auth_header_type=AuthHeaderType.BEARER,
                                       content_type=ContentType.JSON,
                                       data=pdf_payload,
                                       raise_for_status=True,
                                       additional_headers={'Accept': 'application/pdf'})
    pdf_attachment = None
    if report_response.status_code != 200:
        logger.error('Failed to get pdf')
    else:
        pdf_attachment = base64.b64encode(report_response.content)

    return pdf_attachment

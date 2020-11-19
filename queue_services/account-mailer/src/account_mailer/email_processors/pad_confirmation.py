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
"""A Template for the pad confirmation email."""

import base64
import datetime
from pathlib import Path

from auth_api.models import User as UserModel
from auth_api.services.rest_service import RestService
from auth_api.utils.enums import AuthHeaderType, ContentType, Status
from auth_api.utils.roles import ADMIN
from entity_queue_common.service_utils import logger
from flask import current_app
from jinja2 import Template

from account_mailer.email_processors import substitute_template_parts


def process(email_msg: dict,token:str) -> dict:
    """Build the email for PAD Confirmation notification."""
    logger.debug('email_msg notification: %s', email_msg)
    # fill in template

    pdf_attachment = _get_pad_confirmation_report_pdf(email_msg ,token)
    html_body = _get_pad_confirmation_email_body(email_msg)
    return {
        'recipients': _get_admin_emails(email_msg),
        'content': {
            'subject': 'Payment Complete',
            'body': f'{html_body}',
            'attachments': [
                {
                    'fileName': 'PAD_Confirmation_Letter.pdf',
                    'fileBytes': pdf_attachment.decode('utf-8'),
                    'fileUrl': '',
                    'attachOrder': '1'
                }
            ]
        }
    }

def _get_admin_emails(email_msg):
    admin_list = UserModel.find_users_by_org_id_by_status_by_roles(email_msg.get('accountId'), (ADMIN),
                                                                   Status.ACTIVE.value)
    admin_emails = ','.join([str(x.contacts[0].contact.email) for x in admin_list if x.contacts])
    admin_emails = 'sa@fg.asomc'
    return admin_emails

def _get_pad_confirmation_email_body(email_msg):
    body_template = Path(f'{current_app.config.get("TEMPLATE_PATH")}/PAD_CONFIRMATION.html').read_text()
    filled_template = substitute_template_parts(body_template)

    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    html_out = jnja_template.render(
        request=email_msg
    )
    return html_out


def _get_pad_confirmation_report_pdf(email_msg,token):
    current_time = datetime.datetime.now()
    template_vars = {
        **email_msg,
        'generatedDate': current_time.strftime('%m-%d-%Y')
    }
    template = Path(f'{current_app.config.get("PDF_TEMPLATE_PATH")}/pad_confirmation.html').read_text()
    template_b64 = "'" + base64.b64encode(bytes(template, 'utf-8')).decode() + "'"

    pdf_payload = {
        'reportName': 'PAD_Confirmation_Letter',
        'template': template_b64,
        'templateVars': template_vars,
        'populatePageNumber': False,
        'reportName': 'PAD_Confirmation_Letter'
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
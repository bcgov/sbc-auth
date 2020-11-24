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

from flask import current_app
from jinja2 import Template

from auth_api.models import User as UserModel
from auth_api.services.org import Org as OrgService
from auth_api.services.rest_service import RestService
from auth_api.utils.enums import AuthHeaderType, ContentType, Status
from auth_api.utils.roles import ADMIN
from entity_queue_common.service_utils import logger

from account_mailer.email_processors import generate_template


def process(email_msg: dict, token: str) -> dict:
    """Build the email for PAD Confirmation notification."""
    logger.debug('email_msg notification: %s', email_msg)
    # fill in template

    account_id = email_msg.get('accountId')
    admin_emails, admin_name = _get_admin_emails(account_id)
    pdf_attachment = _get_pad_confirmation_report_pdf(email_msg, token)
    html_body = _get_pad_confirmation_email_body(email_msg, admin_name)
    return {
        'recipients': admin_emails,
        'content': {
            'subject': 'Confirmation of Pre-Authorized Debit (PAD) Sign-up',
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


def _get_admin_emails(account_id):
    admin_list = UserModel.find_users_by_org_id_by_status_by_roles(account_id, (ADMIN,),
                                                                   Status.ACTIVE.value)
    admin_emails = ','.join([str(x.contacts[0].contact.email) for x in admin_list if x.contacts])
    admin_name = ' '  # TODO: need to add proper admin name once we figure out the proper way
    return admin_emails, admin_name


def _get_pad_confirmation_email_body(email_msg, admin_name):
    filled_template = generate_template(current_app.config.get("TEMPLATE_PATH"), 'pad_confirmation_email')
    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    html_out = jnja_template.render(
        request=email_msg, admin_name=admin_name

    )
    return html_out


def _get_address(account_id: str):
    mailing_address = OrgService.get_contacts(account_id)
    return mailing_address.get('contacts')[0]


def _get_pad_confirmation_report_pdf(email_msg, token):
    current_time = datetime.datetime.now()
    mailing_address = _get_address(email_msg.get('accountId'))
    template_vars = {
        **email_msg,
        'generatedDate': current_time.strftime('%m-%d-%Y'),
        'accountAddress': mailing_address
    }
    filled_template = generate_template(current_app.config.get("PDF_TEMPLATE_PATH"), 'pad_confirmation')
    template_b64 = "'" + base64.b64encode(bytes(filled_template, 'utf-8')).decode() + "'"

    pdf_payload = {
        'reportName': 'PAD_Confirmation_Letter',
        'template': template_b64,
        'templateVars': template_vars,
        'populatePageNumber': True,
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

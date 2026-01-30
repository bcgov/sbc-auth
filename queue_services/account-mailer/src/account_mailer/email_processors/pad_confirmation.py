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

from auth_api.models import User as UserModel
from auth_api.services.org import Org as OrgService
from flask import current_app
from jinja2 import Template

from account_mailer.email_processors import generate_template
from account_mailer.email_processors.utils import get_account_info
from account_mailer.pdf_utils import get_pdf_from_report_api, get_pdf_from_storage


def process(email_msg: dict, org_id: str, token: str) -> dict:
    """Build the email for PAD Confirmation notification."""
    current_app.logger.debug("email_msg notification: %s", email_msg)
    _, account_name_with_branch = get_account_info(org_id)
    username = email_msg.get("padTosAcceptedBy")
    pad_tos_file_name = current_app.config["PAD_TOS_FILE"]
    admin_emails, admin_name = _get_admin_emails(username)
    pdf_attachment = _get_pad_confirmation_report_pdf(email_msg, token)
    tos_attachment = _get_pdf(pad_tos_file_name)
    html_body = _get_pad_confirmation_email_body(email_msg, admin_name, account_name_with_branch, org_id)
    return {
        "recipients": admin_emails,
        "content": {
            "subject": "Confirmation of Pre-Authorized Debit (PAD) Sign-up",
            "body": f"{html_body}",
            "attachments": [
                {
                    "fileName": "PAD_Confirmation_Letter.pdf",
                    "fileBytes": pdf_attachment.decode("utf-8"),
                    "fileUrl": "",
                    "attachOrder": "1",
                },
                {
                    "fileName": pad_tos_file_name,
                    "fileBytes": tos_attachment.decode("utf-8"),
                    "fileUrl": "",
                    "attachOrder": "2",
                },
            ],
        },
    }


def _get_admin_emails(username):
    admin_user = UserModel.find_by_username(username)
    if admin_user:
        admin_name = admin_user.firstname + " " + admin_user.lastname
        if admin_user.contacts:
            admin_emails = admin_user.contacts[0].contact.email
        else:
            admin_emails = admin_user.email
    else:
        raise ValueError("Admin user not found, cannot determine email address.")

    return admin_emails, admin_name


def _get_pad_confirmation_email_body(email_msg, admin_name, account_name_with_branch, account_number):
    filled_template = generate_template(current_app.config.get("TEMPLATE_PATH"), "pad_confirmation_email")
    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    html_out = jnja_template.render(
        request=email_msg,
        admin_name=admin_name,
        logo_url=email_msg.get("logo_url"),
        account_name_with_branch=account_name_with_branch,
        account_number=account_number,
    )
    return html_out


def _get_address(account_id: str):
    mailing_address = OrgService.get_contacts(account_id)
    return mailing_address.get("contacts")[0]


def _get_pad_confirmation_report_pdf(email_msg, token):
    current_time = datetime.datetime.now()
    mailing_address = _get_address(email_msg.get("accountId"))
    template_vars = {
        **email_msg,
        "generatedDate": current_time.strftime("%m-%d-%Y"),
        "accountAddress": mailing_address,
        "logo_url": email_msg.get("logo_url"),
        "registry_logo_url": email_msg.get("registry_logo_url"),
    }
    filled_template = generate_template(current_app.config.get("PDF_TEMPLATE_PATH"), "pad_confirmation")
    template_b64 = "'" + base64.b64encode(bytes(filled_template, "utf-8")).decode() + "'"

    pdf_payload = {
        "reportName": "PAD_Confirmation_Letter",
        "template": template_b64,
        "templateVars": template_vars,
        "populatePageNumber": True,
    }

    return get_pdf_from_report_api(pdf_payload, token)


def _get_pdf(pad_tos_file_name: str):
    return get_pdf_from_storage(pad_tos_file_name)

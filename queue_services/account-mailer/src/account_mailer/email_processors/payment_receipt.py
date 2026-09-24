# Copyright © 2026 Province of British Columbia
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
"""Build the receipt email sent once a payment settles."""

from auth_api.utils.roles import ADMIN, COORDINATOR
from flask import current_app
from jinja2 import Template

from account_mailer.auth_utils import get_member_emails, get_transaction_url
from account_mailer.email_processors import generate_template
from account_mailer.email_processors.utils import get_account_info
from account_mailer.enums import SubjectType, TemplateType
from account_mailer.pdf_utils import get_pdf_from_report_api


def process(email_msg: dict, token: str) -> dict | None:
    """Build the receipt email, or None when there is nobody to send it to.

    pay-api sends everything it knows: the display fields and the receipt's report-api
    `templateVars`. An express-checkout guest has no `accountId`, so it goes to the
    address the partner supplied and the template drops the account rows.
    """
    org_id = email_msg.get("accountId")
    invoice_id = email_msg.get("invoiceId")
    recipients = get_member_emails(org_id, (ADMIN, COORDINATOR)) if org_id else email_msg.get("emailAddresses")
    if not recipients:
        current_app.logger.info("No one to send the receipt for invoice %s to; skipping.", invoice_id)
        return None

    _, account_name_with_branch = get_account_info(org_id)
    filled_template = generate_template(
        current_app.config.get("TEMPLATE_PATH"), TemplateType.PAYMENT_RECEIPT_TEMPLATE_NAME.value
    )
    html_body = Template(filled_template, autoescape=True).render(
        amount=email_msg.get("amount"),
        account_number=org_id,
        account_name_with_branch=account_name_with_branch,
        invoice_number=email_msg.get("invoiceNumber"),
        payment_method=email_msg.get("paymentMethod"),
        transaction_detail=email_msg.get("transactionDetail"),
        transaction_date=email_msg.get("transactionDate"),
        transactions_url=get_transaction_url(org_id) if org_id else "",
    )
    return {
        "recipients": recipients,
        "content": {
            "subject": SubjectType.PAYMENT_RECEIPT.value.format(invoice_id=invoice_id),
            "body": html_body,
            "attachments": _receipt_attachment(email_msg, token),
        },
    }


def _receipt_attachment(email_msg: dict, token: str) -> list[dict]:
    """Render the receipt PDF, or [] if report-api can't.

    An email without it beats no email — the body already says a pending receipt will follow.
    """
    invoice_id = email_msg.get("invoiceId")
    if not (template_vars := email_msg.get("templateVars")):
        return []
    try:
        pdf = get_pdf_from_report_api(
            {
                "templateName": "payment_receipt",
                "reportName": f"bcregistry-receipt-{invoice_id}",
                "templateVars": template_vars,
            },
            token,
        )
    except Exception:  # NOQA # pylint: disable=broad-except
        current_app.logger.exception("Could not build the receipt attachment for invoice %s", invoice_id)
        return []
    if not pdf:
        return []
    return [{"fileName": f"bcregistry-receipt-{invoice_id}.pdf", "fileBytes": pdf.decode("utf-8"), "attachOrder": "1"}]

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
"""A Template for the account suspended email."""
from auth_api.models import Org as OrgModel
from auth_api.models import Entity as EntityModel 
from flask import current_app
from jinja2 import Template
from structured_logging import StructuredLogging

from account_mailer.auth_utils import get_dashboard_url, get_login_url, get_payment_statements_url
from account_mailer.email_processors import generate_template

logger = StructuredLogging.get_logger()


def process(org_id, recipients, template_name, subject, logo_url, **kwargs) -> dict:
    """Build the email for Account notification."""
    logger.debug("account  notification: %s", org_id)

    account_name: str = None
    account_name_with_branch: str = None
    if org_id:
        org: OrgModel = OrgModel.find_by_id(org_id)
        entity: EntityModel = EntityModel.find_by_entity_id(org_id)
        business_identifier = entity.business_identifier
        account_name = org.name
        account_name_with_branch = org.name
        if org.branch_name:
            account_name_with_branch = f"{org.name} - {org.branch_name}"

    # fill in template
    filled_template = generate_template(current_app.config.get("TEMPLATE_PATH"), template_name)
    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    jinja_kwargs = {
        "account_name": account_name,
        "account_name_with_branch": account_name_with_branch,
        "account_number": org_id,
        "business_identifier": business_identifier,
        "url": get_login_url(),
        "logo_url": logo_url,
        "dashboard_url": get_dashboard_url(),
        "payment_statement_url": get_payment_statements_url(org_id),
        **kwargs,
    }
    logger.debug("notification args: %s", jinja_kwargs)

    html_out = jnja_template.render(jinja_kwargs)

    return {
        "recipients": recipients,
        "content": {"subject": subject, "body": html_out, "attachments": []},
    }

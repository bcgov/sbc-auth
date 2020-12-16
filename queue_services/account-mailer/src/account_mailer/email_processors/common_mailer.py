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
from entity_queue_common.service_utils import logger
from flask import current_app
from jinja2 import Template

from account_mailer.auth_utils import get_login_url
from account_mailer.email_processors import generate_template


def process(org_id, recipients, template_name, subject) -> dict:
    """Build the email for Account notification."""
    logger.debug('account  notification: %s', org_id)

    org: OrgModel = OrgModel.find_by_id(org_id)
    # fill in template
    filled_template = generate_template(current_app.config.get('TEMPLATE_PATH'), template_name, )

    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    html_out = jnja_template.render(
        account_name=org.name, url=get_login_url
    )
    return {
        'recipients': recipients,
        'content': {
            'subject': subject,
            'body': html_out,
            'attachments': []
        }
    }

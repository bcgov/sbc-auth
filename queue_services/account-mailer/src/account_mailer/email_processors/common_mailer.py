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
from datetime import datetime

from auth_api.models import Org as OrgModel
from entity_queue_common.service_utils import logger
from flask import current_app
from jinja2 import Template

from account_mailer.auth_utils import get_login_url
from account_mailer.email_processors import generate_template
from account_mailer.utils import get_local_formatted_date


def process(org_id, recipients, template_name, subject, logo_url, **kwargs) -> dict:
    """Build the email for Account notification."""
    logger.debug('account  notification: %s', org_id)

    account_name: str = None
    if org_id:
        org: OrgModel = OrgModel.find_by_id(org_id)
        account_name = org.name

    # fill in template
    filled_template = generate_template(current_app.config.get('TEMPLATE_PATH'), template_name)
    current_time = datetime.now()
    formatted_date = get_local_formatted_date(current_time, '%m-%d-%Y')
    logger.debug('formatted_date: %s', formatted_date)
    logger.debug('current_time: %s', current_time)
    logger.debug('current_time formatted: %s', current_time.strftime('%m-%d-%Y'))
    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    jinja_kwargs = {
        'account_name': account_name,
        'url': get_login_url(),
        'today': formatted_date,
        'logo_url': logo_url,
        **kwargs
    }

    html_out = jnja_template.render(jinja_kwargs)

    return {
        'recipients': recipients,
        'content': {
            'subject': subject,
            'body': html_out,
            'attachments': []
        }
    }

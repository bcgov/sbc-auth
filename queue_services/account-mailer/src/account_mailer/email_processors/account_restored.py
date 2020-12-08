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
"""A Template for the account restored email."""

from flask import current_app
from jinja2 import Template

from auth_api.models import User as UserModel
from auth_api.utils.roles import ADMIN, COORDINATOR
from auth_api.utils.enums import Status
from entity_queue_common.service_utils import logger
from account_mailer.email_processors import generate_template


def process(email_msg: dict) -> dict:
    """Build the email for Account Restored notification."""
    logger.debug('account restored notification: %s', email_msg)

    account_id = email_msg.get('accountId')
    admin_emails = _get_admin_emails(email_msg.get(account_id))

    # fill in template
    filled_template = generate_template(current_app.config.get("TEMPLATE_PATH"), "account_restored_email")

    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    html_out = jnja_template.render(
        account_name=email_msg.get("accountName"), url='login_url'  # map login url
    )
    return {
        'recipients': admin_emails,
        'content': {
            'subject': 'Your account has been restored.',
            'body': html_out,
            'attachments': []
        }
    }


def _get_admin_emails(account_id):
    admin_list = UserModel.find_users_by_org_id_by_status_by_roles(account_id, (ADMIN, COORDINATOR,),
                                                                   Status.ACTIVE.value)
    admin_emails = ','.join([str(x.contacts[0].contact.email) for x in admin_list if x.contacts])
    return admin_emails

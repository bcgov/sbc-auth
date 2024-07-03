# Copyright © 2024 Province of British Columbia
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
"""A Template for the CSV Failure email."""

from flask import current_app
from jinja2 import Template

from account_mailer.email_processors import generate_template
from account_mailer.enums import SubjectType, TemplateType


def process(email_msg: dict) -> dict:
    """Build the email for CSV failures."""
    current_app.logger.debug('csv_failures: %s', email_msg)
    # fill in template
    bcol_admin_email = current_app.config['BCOL_ADMIN_EMAIL']
    html_body = _get_body(email_msg)
    return {
        'recipients': bcol_admin_email,
        'content': {
            'subject': SubjectType.CSV_FAILED.value,
            'body': f'{html_body}'
        }
    }


def _get_body(email_msg: dict):
    filled_template = generate_template(current_app.config.get('TEMPLATE_PATH'),
                                        TemplateType.CSV_FAILED_TEMPLATE_NAME.value)
    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    html_out = jnja_template.render(
        file_name=email_msg.get('fileName'),
        minio_location=email_msg.get('minioLocation'),
        error_messages=email_msg.get('errorMessages')
    )
    return html_out

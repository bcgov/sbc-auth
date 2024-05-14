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
"""A Template for the EJV Failure email."""

import base64

from flask import current_app
from jinja2 import Template

from account_mailer.email_processors import generate_template
from account_mailer.enums import SubjectType, TemplateType
from account_mailer.services import minio_service


def process(email_msg: dict) -> dict:
    """Build the email for JV failures."""
    current_app.logger.debug('ejv_failures: %s', email_msg)
    # fill in template
    failed_jv_file_name = email_msg.get('fileName')
    file_location = email_msg.get('minioLocation')
    bcol_admin_email = current_app.config['BCOL_ADMIN_EMAIL']
    feedback_attachment = _get_jv_file(file_location, failed_jv_file_name)
    html_body = _get_body(email_msg)
    return {
        'recipients': bcol_admin_email,
        'content': {
            'subject': SubjectType.EJV_FAILED.value,
            'body': f'{html_body}',
            'attachments': [
                {
                    'fileName': failed_jv_file_name,
                    'fileBytes': feedback_attachment.decode('utf-8'),
                    'fileUrl': '',
                    'attachOrder': '1'
                }
            ]
        }
    }


def _get_body(email_msg: dict):
    filled_template = generate_template(current_app.config.get('TEMPLATE_PATH'),
                                        TemplateType.EJV_FAILED_TEMPLATE_NAME.value)
    # render template with vars from email msg
    jnja_template = Template(filled_template, autoescape=True)
    html_out = jnja_template.render(
        logo_url=email_msg.get('logo_url')
    )
    return html_out


def _get_jv_file(file_location: str, file_name: str):
    file = None
    mino_object = minio_service.MinioService.get_minio_file(file_location, file_name)
    if mino_object:
        file = base64.b64encode(mino_object.data)

    return file

# Copyright © 2023 Province of British Columbia
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
"""A processor for the product confirmation email."""

import base64

from flask import current_app

from account_mailer.enums import AttachmentTypes
from account_mailer.services import minio_service


def process_attachment(email_dict: dict, attachment_type: str) -> dict:
    """Process any attachments for a product confirmation notification."""
    if attachment_type is None:
        return email_dict

    attachment_name = _get_attachment_name(attachment_type)

    if attachment_name is None:
        return email_dict

    pdf_attachment = _get_pdf(attachment_name)
    email_dict['content']['attachments'] = [
        {
            'fileName': attachment_name,
            'fileBytes': pdf_attachment.decode('utf-8'),
            'fileUrl': '',
            'attachOrder': '1'
        }
    ]

    return email_dict


def _get_attachment_name(attachment_type: str) -> str:
    if attachment_type == AttachmentTypes.QUALIFIED_SUPPLIER.value:
        return current_app.config['MHR_QS_AGREEMENT_FILE']

    return None


def _get_pdf(file_name: str):
    read_pdf = None
    mino_object = minio_service.MinioService.get_minio_file(current_app.config['MINIO_BUCKET'],
                                                            file_name)
    if mino_object:
        read_pdf = base64.b64encode(mino_object.data)

    return read_pdf

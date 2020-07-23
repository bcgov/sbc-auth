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

"""Attachment factory."""
import base64
from enum import Enum

from faker import Factory as FakerFactory

from notify_api.db.models import AttachmentModel


faker = FakerFactory.create()


class AttachmentFactory():   # pylint: disable=too-few-public-methods
    """Attachment factory."""

    class Models(dict, Enum):
        """Attachment model data."""

        FILE_1 = {'id': 1,
                  'file_name': 'aaa.text',
                  'file_bytes': 'SGVsbG8gV29ybGQgYnkgdHh0ICEhIQ==',
                  'attach_order': 1}

        FILE_2 = {'id': 2,
                  'file_name': 'bbb.text',
                  'file_bytes': 'SGVsbG8gV29ybGQgYnkgdHh0ICEhIQ==',
                  'attach_order': 2}

    class RequestData(dict, Enum):
        """Attachment post request payload data."""

        FILE_REQUEST_1 = {'fileName': 'aaa.pdf',
                          'fileBytes': '',
                          'fileUrl': 'https://minio-dev.pathfinder.gov.bc.ca/public/affidavit_v1.pdf',
                          'attachOrder': 1}

        FILE_REQUEST_2 = {'fileName': 'bbb.text',
                          'fileBytes': 'SGVsbG8gV29ybGQgYnkgdHh0ICEhIQ==',
                          'fileUrl': '',
                          'attachOrder': 2}

    class RequestBadData(dict, Enum):
        """Attachment post payload with inconsistent data."""

        # name empty
        FILE_REQUEST_BAD_1 = {'fileName': '',
                              'fileBytes': '',
                              'fileUrl': 'https://minio-dev.pathfinder.gov.bc.ca/public/affidavit_v1.pdf',
                              'attachOrder': 1}

        # without name
        FILE_REQUEST_BAD_2 = {'fileBytes': '',
                              'fileUrl': 'https://minio-dev.pathfinder.gov.bc.ca/public/affidavit_v1.pdf',
                              'attachOrder': 1}

        # file content empty
        FILE_REQUEST_BAD_3 = {'fileName': 'aaa.pdf',
                              'fileBytes': '',
                              'fileUrl': '',
                              'attachOrder': 1}

        # without file content
        FILE_REQUEST_BAD_4 = {'fileName': 'aaa.pdf',
                              'fileBytes': '',
                              'attachOrder': 1}

        # without file content
        FILE_REQUEST_BAD_5 = {'fileName': 'aaa.pdf',
                              'fileUrl': '',
                              'attachOrder': 1}

        # without file content
        FILE_REQUEST_BAD_6 = {'fileName': 'aaa.pdf',
                              'attachOrder': 1}

    @ staticmethod
    def create_model(session,
                     content_id: int = 1,
                     attachment_info: dict = Models.FILE_1):
        """Produce an attachment model."""
        attachment = AttachmentModel(id=attachment_info['id'],
                                     file_name=attachment_info['file_name'],
                                     file_bytes=base64.b64decode(attachment_info['file_bytes']),
                                     attach_order=attachment_info['attach_order'],
                                     content_id=content_id)
        session.add(attachment)
        session.commit()
        attachment = session.merge(attachment)

        return attachment

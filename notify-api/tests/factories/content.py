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

"""Conent factory."""
from enum import Enum

from faker import Factory as FakerFactory

from notify_api.db.models import ContentModel
from tests.factories.attachment import AttachmentFactory


faker = FakerFactory.create()


class ContentFactory():   # pylint: disable=too-few-public-methods
    """Content factory."""

    class Models(dict, Enum):
        """Content model data."""

        CONTENT_1 = {'id': 1,
                     'subject': faker.text(),
                     'body': faker.text()}

    class RequestData(dict, Enum):
        """Content post request payload data."""

        CONTENT_REQUEST_1 = {'subject': faker.text(),
                             'body': faker.text()}

        CONTENT_REQUEST_2 = {'subject': faker.text(),
                             'body': faker.text(),
                             'attachments': [AttachmentFactory.RequestData.FILE_REQUEST_1]}

        CONTENT_REQUEST_3 = {'subject': faker.text(),
                             'body': faker.text(),
                             'attachments': [AttachmentFactory.RequestData.FILE_REQUEST_1,
                                             AttachmentFactory.RequestData.FILE_REQUEST_2]}

    class RequestBadData(dict, Enum):
        """Content post payload with inconsistent data."""

        # subject empty
        CONTENT_REQUEST_BAD_1 = {'subject': '',
                                 'body': faker.text()}

        # without subject
        CONTENT_REQUEST_BAD_2 = {'body': faker.text()}

        # without body
        CONTENT_REQUEST_BAD_3 = {'subject': faker.text()}

    @ staticmethod
    def create_model(session,
                     notification_id: int = 1,
                     content_info: dict = Models.CONTENT_1):
        """Produce a content model."""
        content = ContentModel(id=content_info['id'],
                               subject=content_info['subject'],
                               body=content_info['body'],
                               notification_id=notification_id)
        session.add(content)
        session.commit()
        content = session.merge(content)

        return content

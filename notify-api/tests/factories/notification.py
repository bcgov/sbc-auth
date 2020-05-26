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

"""notification factory."""
from datetime import datetime, timedelta
from enum import Enum

from faker import Factory as FakerFactory

from notify_api.db.models import NotificationModel
from notify_api.db.models.notification_status import NotificationStatusEnum
from notify_api.db.models.notification_type import NotificationTypeEnum
from tests.factories.attachment import AttachmentFactory
from tests.factories.content import ContentFactory


faker = FakerFactory.create()


class NotificationFactory():  # pylint: disable=too-few-public-methods
    """notification factory."""

    class Models(dict, Enum):
        """Notification model data."""

        PENDING_1 = {'id': 1,
                     'recipients': faker.safe_email(),
                     'request_date': faker.date_time(),
                     'request_by': faker.user_name(),
                     'type_code': NotificationTypeEnum.EMAIL,
                     'status_code': NotificationStatusEnum.PENDING}

        PENDING_2 = {'id': 2,
                     'recipients': faker.safe_email(),
                     'request_date': faker.date_time(),
                     'request_by': faker.user_name(),
                     'type_code': NotificationTypeEnum.EMAIL,
                     'status_code': NotificationStatusEnum.PENDING}

        LESS_1_HOUR = {'id': 1,
                       'recipients': faker.safe_email(),
                       'request_date': datetime.utcnow() - timedelta(hours=1),
                       'request_by': faker.user_name(),
                       'type_code': NotificationTypeEnum.EMAIL,
                       'status_code': NotificationStatusEnum.FAILURE}

        OVER_1_HOUR = {'id': 1,
                       'recipients': faker.safe_email(),
                       'request_date': datetime.utcnow() - timedelta(hours=10),
                       'request_by': faker.user_name(),
                       'type_code': NotificationTypeEnum.EMAIL,
                       'status_code': NotificationStatusEnum.FAILURE}

    class RequestData(dict, Enum):
        """Notification post request payload data."""

        REQUEST_1 = {'recipients': faker.safe_email(),
                     'requestBy': faker.user_name(),
                     'content': ContentFactory.RequestData.CONTENT_REQUEST_1}

        REQUEST_2 = {'recipients': faker.safe_email(),
                     'requestBy': faker.user_name(),
                     'content': ContentFactory.RequestData.CONTENT_REQUEST_2}

        REQUEST_3 = {'recipients': faker.safe_email(),
                     'requestBy': faker.user_name(),
                     'content': ContentFactory.RequestData.CONTENT_REQUEST_3}

    class RequestBadData(dict, Enum):
        """Notification post payload with inconsistent data."""

        # email empty
        REQUEST_BAD_1 = {'recipients': '',
                         'requestBy': faker.user_name(),
                         'content': ContentFactory.RequestData.CONTENT_REQUEST_1}

        # without email
        REQUEST_BAD_2 = {'requestBy': faker.user_name(),
                         'content': ContentFactory.RequestData.CONTENT_REQUEST_1}
        # bad email
        REQUEST_BAD_3 = {'recipients': 'aaa',
                         'requestBy': faker.user_name(),
                         'content': ContentFactory.RequestData.CONTENT_REQUEST_1}
        # bad email
        REQUEST_BAD_4 = {'recipients': 'aaa@aaa.com, bbbb',
                         'requestBy': faker.user_name(),
                         'content': ContentFactory.RequestData.CONTENT_REQUEST_1}
        # bad email
        REQUEST_BAD_5 = {'recipients': 'aaa@aaa.com, bbbb@bbb',
                         'requestBy': faker.user_name(),
                         'content': ContentFactory.RequestData.CONTENT_REQUEST_1}
        # bad email
        REQUEST_BAD_6 = {'recipients': 'aaa.com, bbbb@bbb.com',
                         'requestBy': faker.user_name(),
                         'content': ContentFactory.RequestData.CONTENT_REQUEST_1}
        # subject empty
        REQUEST_BAD_7 = {'recipients': faker.safe_email(),
                         'requestBy': faker.user_name(),
                         'content': ContentFactory.RequestBadData.CONTENT_REQUEST_BAD_1}
        # without subject
        REQUEST_BAD_8 = {'recipients': faker.safe_email(),
                         'requestBy': faker.user_name(),
                         'content': ContentFactory.RequestBadData.CONTENT_REQUEST_BAD_2}
        # without body
        REQUEST_BAD_9 = {'recipients': faker.safe_email(),
                         'requestBy': faker.user_name(),
                         'content': ContentFactory.RequestBadData.CONTENT_REQUEST_BAD_3}
        # name empty
        REQUEST_BAD_10 = {'recipients': faker.safe_email(),
                          'requestBy': faker.user_name(),
                          'content': {'subject': faker.text(),
                                      'body': faker.text(),
                                      'attachments': [AttachmentFactory.RequestBadData.FILE_REQUEST_BAD_1]}}
        # without name
        REQUEST_BAD_11 = {'recipients': faker.safe_email(),
                          'requestBy': faker.user_name(),
                          'content': {'subject': faker.text(),
                                      'body': faker.text(),
                                      'attachments': [AttachmentFactory.RequestBadData.FILE_REQUEST_BAD_2]}}
        # file content empty
        REQUEST_BAD_12 = {'recipients': faker.safe_email(),
                          'requestBy': faker.user_name(),
                          'content': {'subject': faker.text(),
                                      'body': faker.text(),
                                      'attachments': [AttachmentFactory.RequestBadData.FILE_REQUEST_BAD_3]}}
        # without file content
        REQUEST_BAD_13 = {'recipients': faker.safe_email(),
                          'requestBy': faker.user_name(),
                          'content': {'subject': faker.text(),
                                      'body': faker.text(),
                                      'attachments': [AttachmentFactory.RequestBadData.FILE_REQUEST_BAD_4]}}
        # without file content
        REQUEST_BAD_14 = {'recipients': faker.safe_email(),
                          'requestBy': faker.user_name(),
                          'content': {'subject': faker.text(),
                                      'body': faker.text(),
                                      'attachments': [AttachmentFactory.RequestBadData.FILE_REQUEST_BAD_5]}}
        # without file content
        REQUEST_BAD_15 = {'recipients': faker.safe_email(),
                          'requestBy': faker.user_name(),
                          'content': {'subject': faker.text(),
                                      'body': faker.text(),
                                      'attachments': [AttachmentFactory.RequestBadData.FILE_REQUEST_BAD_6]}}

    @ staticmethod
    def create_model(session, notification_info: dict = Models.PENDING_1):
        """Produce a notification model."""
        notification = NotificationModel(recipients=notification_info['recipients'],
                                         request_date=notification_info['request_date'],
                                         request_by=notification_info['request_by'],
                                         type_code=notification_info['type_code'],
                                         status_code=notification_info.get('status_code', None))
        session.add(notification)
        session.commit()
        notification = session.merge(notification)

        return notification

# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Notification contents CRUD."""
import base64
from sqlalchemy.orm import Session
from notify_api.core.utils import download_file
from notify_api.db.models.notification_contents import NotificationContentsModel, NotificationContentsRequest


async def find_contents_by_id(db_session: Session, content_id: int):
    """get notification contents by id."""
    db_notification = db_session.query(NotificationContentsModel)\
        .filter(NotificationContentsModel.id == content_id).first()
    return db_notification


async def find_contents_by_notification_id(db_session: Session, notification_id: int):
    """get notification contents by notification id."""
    db_notification = db_session.query(NotificationContentsModel) \
        .filter(NotificationContentsModel.notification_id == notification_id).first()
    return db_notification


async def create_contents(db_session: Session, contents: NotificationContentsRequest, notification_id: int):
    """create notification contents."""
    file_name = None
    file_bytes = None

    if contents.attachment_url:
        file_name = contents.attachment_name
        file_bytes = download_file(contents.attachment_url)
    else:
        if contents.attachment_bytes:
            file_name = contents.attachment_name
            file_bytes = base64.b64decode(contents.attachment_bytes)

    db_contents = NotificationContentsModel(subject=contents.subject,
                                            body=contents.body,
                                            notification_id=notification_id,
                                            attachment_name=file_name,
                                            attachment=file_bytes)
    db_session.add(db_contents)
    db_session.commit()
    db_session.refresh(db_contents)
    return db_contents

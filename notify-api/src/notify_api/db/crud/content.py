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
"""Notification content CRUD."""
from sqlalchemy.orm import Session

from notify_api.db.crud import attachment as AttachmentCRUD
from notify_api.db.models.content import ContentModel, ContentRequest, ContentUpdate


async def find_content_by_id(db_session: Session, content_id: int):
    """Get notification content by id."""
    db_content = db_session.query(ContentModel)\
        .filter(ContentModel.id == content_id).first()
    return db_content


async def find_content_by_notification_id(db_session: Session, notification_id: int):
    """Get notification content by notification id."""
    db_content = db_session.query(ContentModel) \
        .filter(ContentModel.notification_id == notification_id).first()
    return db_content


async def create_content(db_session: Session, content: ContentRequest, notification_id: int):
    """Create notification content."""
    db_content = ContentModel(subject=content.subject,
                              body=content.body,
                              notification_id=notification_id)
    db_session.add(db_content)
    db_session.commit()
    db_session.refresh(db_content)

    if content.attachments:
        for attachment in content.attachments:
            # save email attachment
            await AttachmentCRUD.create_attachment(db_session,
                                                   attachment=attachment,
                                                   content_id=db_content.id)

    return db_content


async def update_content(db_session: Session, content: ContentUpdate):
    """Update content."""
    db_content = content
    db_session.add(db_content)
    db_session.commit()
    db_session.refresh(db_content)
    return db_content

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
"""Notification attachment CRUD."""
import base64

from sqlalchemy.orm import Session

from notify_api.core.utils import download_file
from notify_api.db.models.attachment import AttachmentModel, AttachmentRequest


async def find_attachment_by_id(db_session: Session, attachment_id: int):
    """Get notification attachment by id."""
    db_attachment = db_session.query(AttachmentModel)\
        .filter(AttachmentModel.id == attachment_id).first()
    return db_attachment


async def find_attachments_by_content_id(db_session: Session, content_id: int):
    """Get notification attachment by content id."""
    db_attachments = db_session.query(AttachmentModel) \
        .filter(AttachmentModel.content_id == content_id).order_by(AttachmentModel.attach_order.asc()).all()
    return db_attachments


async def create_attachment(db_session: Session, attachment: AttachmentRequest, content_id: int):
    """Create notification attachment."""
    file_bytes = None

    if attachment.file_url:
        file_bytes = download_file(attachment.file_url)
    else:
        if attachment.file_bytes:
            file_bytes = base64.b64decode(attachment.file_bytes)

    db_attachment = AttachmentModel(content_id=content_id,
                                    file_name=attachment.file_name,
                                    file_bytes=file_bytes,
                                    attach_order=attachment.attach_order)
    db_session.add(db_attachment)
    db_session.commit()
    db_session.refresh(db_attachment)

    return db_attachment

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
"""Table for storing all static documents.

Documents which are static in nature are stored in this table  ie.terms of use
"""

from sqlalchemy import Column, String, Text, desc

from .base_model import BaseModel
from .db import db


class Documents(BaseModel):
    """This is the model for a documents."""

    __tablename__ = 'documents'

    # TODO version concept is not well refined..this is the first version..refine it
    version_id = Column(String(10), primary_key=True, autoincrement=False)
    type = Column('type', String(30), nullable=False)
    content_type = Column('content_type', String(20), nullable=False)
    content = Column('content', Text)

    @classmethod
    def fetch_latest_document_by_type(cls, file_type):
        """Fetch latest document of any time."""
        return db.session.query(Documents).filter(
            Documents.type == file_type).order_by(desc(Documents.version_id)).limit(1).one_or_none()

    @classmethod
    def find_latest_version_by_type(cls, file_type):
        """Fetch latest document of any time."""
        return db.session.query(Documents.version_id).filter(
            Documents.type == file_type).order_by(desc(Documents.version_id)).limit(1).scalar()

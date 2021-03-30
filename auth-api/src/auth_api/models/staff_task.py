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
"""This model manages a Staff Task item in the Auth Service."""

from sqlalchemy import Column, DateTime, Integer, String
from .db import db
from .base_model import BaseModel


class StaffTask(BaseModel):
    """Model for a StaffTask record."""

    __tablename__ = 'staff_tasks'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    date_submitted = Column(DateTime)
    relationship_type = Column(String(50), nullable=False)
    relationship_id = Column(Integer, index=True, nullable=False)
    due_date = Column(DateTime)
    task_type = Column(String(50), nullable=False)

    @classmethod
    def fetch_staff_tasks(cls):
        """Find Org that matches the provided name and not in INACTIVE status."""
        query = db.session.query(StaffTask)
        return query.all()

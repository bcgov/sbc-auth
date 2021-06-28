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
"""This model manages a Task item in the Auth Service."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..utils.enums import TaskRelationshipStatus, TaskStatus
from .base_model import BaseModel
from .db import db


class Task(BaseModel):
    """Model for a Task record."""

    __tablename__ = 'tasks'

    id = Column(Integer, index=True, primary_key=True)
    name = Column(String(250), nullable=False)  # Stores name of the relationship item. For eg, an org name
    date_submitted = Column(DateTime)  # Instance when task is created
    relationship_type = Column(String(50), nullable=False)  # That is to be acted up on. For eg, an org
    relationship_id = Column(Integer, index=True, nullable=False)
    relationship_status = Column(String(100), nullable=True)  # Status of the related object. For eg,
    # org_Status of an org
    due_date = Column(DateTime)  # Optional field
    type = Column(String(50), nullable=False)  # type of the task. For eg, PENDING_STAFF_REVIEW
    status = Column(String(50), nullable=False)  # task is acted or to be acted. can be open or completed
    account_id = Column(Integer, nullable=True)  # account id related to task. Eg,
    # org id for pending product subscriptions
    related_to = Column(ForeignKey('users.id', ondelete='SET NULL',
                                   name='related_to_fkey'), nullable=False)
    # task that is assigned to the particular user
    user = relationship('User', foreign_keys=[related_to], lazy='select')

    @classmethod
    def fetch_tasks(cls, task_type: str, task_status: str,  # pylint:disable=too-many-arguments
                    task_relationship_status: str,
                    page: int, limit: int):
        """Fetch all tasks."""
        query = db.session.query(Task)

        if task_type:
            query = query.filter(Task.type == task_type)
        if task_status:
            query = query.filter(Task.status == task_status)
        if task_relationship_status:
            if task_relationship_status == TaskRelationshipStatus.PENDING_STAFF_REVIEW.value:
                query = query.filter(Task.relationship_status == task_relationship_status).order_by(
                    Task.date_submitted.asc())
            else:
                query = query.filter(Task.relationship_status == task_relationship_status)

        # Add pagination
        pagination = query.paginate(per_page=limit, page=page)
        return pagination.items, pagination.total

    @classmethod
    def find_by_task_id(cls, task_id):
        """Find a task instance that matches the provided id."""
        return db.session.query(Task).filter_by(id=task_id).first()

    @classmethod
    def find_by_task_relationship_id(cls, relationship_id: int, task_relationship_type: str,
                                     task_status: str = TaskStatus.OPEN.value):
        """Find a task instance that related to the relationship id ( may be an ORG or a PRODUCT."""
        return db.session.query(Task).filter(Task.relationship_id == relationship_id,
                                             Task.relationship_type == task_relationship_type,
                                             task_status == task_status).first()

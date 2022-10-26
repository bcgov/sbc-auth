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
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from auth_api.models.dataclass import TaskSearch
from ..utils.enums import TaskRelationshipStatus, TaskRelationshipType, TaskStatus
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
    relationship_status = Column(String(100), nullable=True)  # Status of the related object. e.g, PENDING_STAFF_REVIEW
    due_date = Column(DateTime)  # Optional field
    type = Column(String(50), nullable=False)  # type of the task. For eg, GovN, BCeID Admin, New Account etc.
    action = Column(String(50), nullable=True)  # Any sub type information for the task.
    status = Column(String(50), nullable=False)  # task is acted or to be acted. can be open or completed
    account_id = Column(Integer, nullable=True)  # account id related to task. Eg,
    # org id for pending product subscriptions
    related_to = Column(ForeignKey('users.id', ondelete='SET NULL',
                                   name='related_to_fkey'), nullable=False)
    # python list of remarks <- -> postgres array of remarks
    remarks = Column(ARRAY(String, dimensions=1), nullable=True)

    # task that is assigned to the particular user
    user = relationship('User', foreign_keys=[related_to], lazy='select')

    @classmethod
    def fetch_tasks(cls, task_search: TaskSearch):
        """Fetch all tasks."""
        query = db.session.query(Task)
        if task_search.name:
            query = query.filter(Task.name.ilike(f'%{task_search.name}%'))
        if task_search.type:
            query = query.filter(Task.type == task_search.type)
        if task_search.status:
            query = query.filter(Task.status.in_(task_search.status))
        if task_search.start_date:
            query = query.filter(Task.date_submitted >= task_search.start_date)
        if task_search.end_date:
            query = query.filter(Task.date_submitted <= task_search.end_date)
        if task_search.relationship_status:
            query = query.filter(Task.relationship_status == task_search.relationship_status)
        if task_search.relationship_status == TaskRelationshipStatus.PENDING_STAFF_REVIEW.value:
            query = query.order_by(Task.date_submitted.asc())

        # Add pagination
        pagination = query.paginate(per_page=task_search.limit, page=task_search.page)
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
                                             Task.status == task_status).first()

    @classmethod
    def find_by_task_for_account(cls, org_id, status):
        """Find a task instance that matches the provided id."""
        return db.session.query(Task).filter_by(relationship_id=org_id,
                                                relationship_type=TaskRelationshipType.ORG.value, status=status).first()

    @classmethod
    def find_by_user_and_status(cls, org_id, status):
        """Find a task instance that matches the provided id."""
        return db.session.query(Task).filter_by(account_id=org_id,
                                                relationship_type=TaskRelationshipType.USER.value, status=status)\
            .first()

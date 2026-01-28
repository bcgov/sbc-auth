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

from typing import Self

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from auth_api.models.dataclass import TaskSearch
from auth_api.utils.date import str_to_utc_dt
from auth_api.utils.enums import TaskRelationshipStatus, TaskRelationshipType, TaskStatus

from .base_model import BaseModel
from .db import db


class Task(BaseModel):
    """Model for a Task record."""

    __tablename__ = "tasks"

    id = Column(Integer, index=True, primary_key=True)
    name = Column(String(250), nullable=False)  # Stores name of the relationship item. For eg, an org name
    date_submitted = Column(DateTime)  # Instance when task is created
    external_source_id = Column(String(75), nullable=True)  # Optional external system source identifier
    is_resubmitted = Column(
        Boolean(), default=False, nullable=False
    )  # Stores whether this task is resubmitted for review
    relationship_type = Column(String(50), nullable=False)  # That is to be acted up on. For eg, an org
    relationship_id = Column(Integer, index=True, nullable=False)
    relationship_status = Column(String(100), nullable=True)  # Status of the related object. e.g, PENDING_STAFF_REVIEW
    due_date = Column(DateTime)  # Optional field
    type = Column(String(50), nullable=False)  # type of the task. For eg, GovN, BCeID Admin, New Account etc.
    action = Column(String(50), nullable=True)  # Any sub type information for the task.
    status = Column(String(50), nullable=False)  # task is acted or to be acted. can be open or completed
    account_id = Column(Integer, nullable=True)  # account id related to task. Eg,
    # org id for pending product subscriptions
    related_to = Column(ForeignKey("users.id", ondelete="SET NULL", name="related_to_fkey"), nullable=False)
    # python list of remarks <- -> postgres array of remarks
    remarks = Column(ARRAY(String, dimensions=1), nullable=True)

    # task that is assigned to the particular user
    user = relationship("User", foreign_keys=[related_to], lazy="select")

    @classmethod
    def fetch_tasks(cls, task_search: TaskSearch):
        """Fetch all tasks."""
        query = db.session.query(Task)

        if task_search.name:
            query = query.filter(Task.name.ilike(f"%{task_search.name}%"))
        if task_search.type:
            query = query.filter(Task.type == task_search.type)
        if task_search.status:
            query = query.filter(Task.status.in_(task_search.status))
        if task_search.action:
            query = query.filter(Task.action.in_(task_search.action))
        start_date = None
        end_date = None
        if task_search.start_date:
            start_date = str_to_utc_dt(task_search.start_date, False)
        if task_search.end_date:
            end_date = str_to_utc_dt(task_search.end_date, True)
        if start_date or end_date:
            query = query.filter_conditional_date_range(start_date, end_date, Task.date_submitted, cast_to_date=False)
        if task_search.relationship_status:
            query = query.filter(Task.relationship_status == task_search.relationship_status)
        if task_search.modified_by:
            query = (
                query.join(Task.modified_by)
                .filter(text("lower(users.first_name || ' ' || users.last_name) like lower(:search_text)"))
                .params(search_text=f"%{task_search.modified_by}%")
            )
        if task_search.relationship_status == TaskRelationshipStatus.PENDING_STAFF_REVIEW.value:
            query = query.order_by(Task.date_submitted.asc())
        if task_search.submitted_sort_order == "asc":
            query = query.order_by(Task.date_submitted.asc())
        if task_search.submitted_sort_order == "desc":
            query = query.order_by(Task.date_submitted.desc())

        # Add pagination
        pagination = query.paginate(per_page=task_search.limit, page=task_search.page)
        return pagination.items, pagination.total

    @classmethod
    def find_by_task_id(cls, task_id: int) -> Self:
        """Find a task instance that matches the provided id."""
        return db.session.query(Task).filter_by(id=int(task_id or -1)).first()

    @classmethod
    def find_by_task_relationship_id(
        cls, relationship_id: int, task_relationship_type: str, task_status: str = TaskStatus.OPEN.value
    ) -> Self:
        """Find a task instance that related to the relationship id ( may be an ORG or a PRODUCT."""
        return (
            db.session.query(Task)
            .filter(
                Task.relationship_id == int(relationship_id or -1),
                Task.relationship_type == task_relationship_type,
                Task.status == task_status,
            )
            .first()
        )

    @classmethod
    def find_by_incomplete_task_relationship_id(
        cls, relationship_id: int, task_relationship_type: str, relationship_status: str = None
    ) -> Self:
        """Find a task instance that related to the relationship id ( may be an ORG or a PRODUCT) that is incomplete."""
        query = db.session.query(Task).filter(
            Task.relationship_id == int(relationship_id or -1),
            Task.relationship_type == task_relationship_type,
            Task.status.in_((TaskStatus.OPEN.value, TaskStatus.HOLD.value)),
        )

        if relationship_status is not None:
            query = query.filter(Task.relationship_status == relationship_status)

        return query.first()

    @classmethod
    def find_by_task_for_account(cls, org_id: int, status):
        """Find a task instance that matches the provided id."""
        return (
            db.session.query(Task)
            .filter_by(
                relationship_id=int(org_id or -1), relationship_type=TaskRelationshipType.ORG.value, status=status
            )
            .first()
        )

    @classmethod
    def find_by_user_and_status(cls, org_id: int, status):
        """Find a task instance that matches the provided id."""
        return (
            db.session.query(Task)
            .filter_by(account_id=int(org_id or -1), relationship_type=TaskRelationshipType.USER.value, status=status)
            .first()
        )

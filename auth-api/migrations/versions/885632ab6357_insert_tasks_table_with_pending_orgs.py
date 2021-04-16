"""insert tasks table with pending orgs

Revision ID: 885632ab6357
Revises: d804bcead371
Create Date: 2021-04-13 14:38:09.983595

"""
from typing import List
from alembic import op

from auth_api.models import Org
from auth_api.utils.enums import TaskStatus, TaskRelationshipType, TaskRelationshipStatus, TaskTypePrefix

# revision identifiers, used by Alembic.

revision = '885632ab6357'
down_revision = 'd804bcead371'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    org_res = conn.execute(f"SELECT * FROM orgs WHERE status_code = 'PENDING_STAFF_REVIEW';")
    org_list: List[Org] = org_res.fetchall()

    for org in org_list:
        org_id = org.id
        user_id = org.created_by_id
        created_time = org.created
        date_submitted = org.created
        name = org.name
        status = TaskStatus.OPEN.value
        task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
        relationship_status = TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
        task_relationship_type = TaskRelationshipType.ORG.value

        # Insert into tasks
        op.execute(f"INSERT INTO tasks(created, modified, name, date_submitted, relationship_type, "
                   f"relationship_id, created_by_id, modified_by_id, related_to, status, type, relationship_status)"
                   f"VALUES "
                   f"('{created_time}', '{created_time}', '{name}', '{date_submitted}', '{task_relationship_type}',"
                   f" {org_id}, {user_id}, {user_id}, {user_id}, '{status}', '{task_type}', '{relationship_status}')")

    pass


def downgrade():
    # Delete the tasks
    op.execute(f"DELETE FROM tasks")
    pass

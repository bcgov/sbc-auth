"""insert tasks table with pending orgs

Revision ID: 885632ab6357
Revises: d804bcead371
Create Date: 2021-04-13 14:38:09.983595

"""
from typing import List
from alembic import op
from sqlalchemy import text

from auth_api.models import Org
from auth_api.utils.enums import TaskStatus, TaskRelationshipType, TaskTypePrefix, TaskRelationshipStatus

# revision identifiers, used by Alembic.

revision = '885632ab6357'
down_revision = 'd804bcead371'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

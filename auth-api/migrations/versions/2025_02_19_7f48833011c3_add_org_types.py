"""Add org types for read-only staff.

Revision ID: 7f48833011c3
Revises: 63cfd9b160d7
Create Date: 2025-02-19 15:54:22.459049

"""
from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '7f48833011c3'
down_revision = '63cfd9b160d7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "INSERT INTO org_types (code, description, \"default\") VALUES ('STAFF_READ_ONLY', 'BC Registries Read Only Staff', false)"
    )

def downgrade():
    op.execute("DELETE FROM org_types WHERE code = 'STAFF_READ_ONLY'")

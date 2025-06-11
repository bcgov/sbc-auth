"""Fix remarks size

Revision ID: 8eefa6bf6f05
Revises: 5a5a3a82f05c
Create Date: 2025-06-11 14:52:35.516745

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8eefa6bf6f05'
down_revision = '5a5a3a82f05c'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "tasks",
        "remarks",
        type_=postgresql.ARRAY(sa.String(), dimensions=1),
        existing_nullable=True,
        postgresql_using="remarks::character varying(255)[]",
    )


def downgrade():
    op.alter_column(
        "tasks",
        "remarks",
        type_=postgresql.ARRAY(sa.String(), dimensions=1),
        existing_nullable=True,
        postgresql_using="remarks::character varying(100)[]",
    )

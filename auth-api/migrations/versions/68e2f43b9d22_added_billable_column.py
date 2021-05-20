"""added billable column

Revision ID: 68e2f43b9d22
Revises: abc8cc7b64e1
Create Date: 2020-03-17 23:00:51.705492

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Boolean, Date, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '68e2f43b9d22'
down_revision = 'abc8cc7b64e1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('org', sa.Column('billable', sa.Boolean(), server_default=sa.schema.DefaultClause("1"), nullable=False))


def downgrade():
    op.drop_column('org', 'billable')

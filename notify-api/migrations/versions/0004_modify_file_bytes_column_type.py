"""Modify file_bytes column type

Revision ID: aa4e6bdf1984
Revises: 3c6a5fef5da3
Create Date: 2021-06-28 16:10:18.736866

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa4e6bdf1984'
down_revision = '3c6a5fef5da3'
branch_labels = None
depends_on = None



def upgrade():
    op.alter_column('attachment', 'file_bytes', type_=sa.LargeBinary())


def downgrade():
    op.alter_column('attachment', 'file_bytes', type_=sa.LargeBinary())

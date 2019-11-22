"""Modify email body column type to Text

Revision ID: 59345515423b
Revises: 4273ebef85cc
Create Date: 2019-11-20 09:49:43.803727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59345515423b'
down_revision = '4273ebef85cc'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('notification_contents', 'body', type_=sa.Text())


def downgrade():
    op.alter_column('notification_contents', 'body', type_=sa.String(length=2000))

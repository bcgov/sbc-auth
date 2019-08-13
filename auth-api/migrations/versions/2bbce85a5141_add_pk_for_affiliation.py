"""Add PK for affiliation

Revision ID: 2bbce85a5141
Revises: 6ae6bd8d5033
Create Date: 2019-08-13 14:33:24.989620

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bbce85a5141'
down_revision = '6ae6bd8d5033'
branch_labels = None
depends_on = None


def upgrade():
    op.create_primary_key('pk_affiliation', 'affiliation', ['id'])


def downgrade():
    pass

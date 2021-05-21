"""add_fee_schedule_link

Revision ID: f7362101e761
Revises: 0f310e71e51d
Create Date: 2021-01-06 10:04:25.171025

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Integer, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = 'f7362101e761'
down_revision = '0f310e71e51d'
branch_labels = None
depends_on = None


def upgrade():
    old_content='on the Website[LVAA1][MOU2]'
    new_content='<a href="./price-list" target="_blank">on the Website</a>'

    update_query=f"UPDATE documents SET content = replace(content, '{old_content}', '{new_content}') WHERE version_id='4'"
    op.execute(update_query)


def downgrade():
    pass

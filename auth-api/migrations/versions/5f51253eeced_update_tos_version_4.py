"""update tos version 4

Revision ID: 5f51253eeced
Revises: eaef1147f25c
Create Date: 2021-01-12 16:10:54.633790

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Integer, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '5f51253eeced'
down_revision = 'eaef1147f25c'
branch_labels = None
depends_on = None


def upgrade():
    old_content='<li><span>13.1</span>The Province may'
    new_content='<li><span>13.3</span>The Province may'

    update_query=f"UPDATE documents SET content = replace(content, '{old_content}', '{new_content}') WHERE version_id='4' AND type='termsofuse'"
    op.execute(update_query)

    old_content='<li><span>13.3</span>In the event of'
    new_content='<li><span>13.4</span>In the event of'

    update_query=f"UPDATE documents SET content = replace(content, '{old_content}', '{new_content}') WHERE version_id='4' AND type='termsofuse'"
    op.execute(update_query)

def downgrade():
    pass

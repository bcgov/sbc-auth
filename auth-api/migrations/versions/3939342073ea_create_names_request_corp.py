"""create_names_request_corp

Revision ID: 3939342073ea
Revises: 243d9782085e
Create Date: 2020-03-06 09:49:52.760695

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '3939342073ea'
down_revision = '243d9782085e'
branch_labels = None
depends_on = None


def upgrade():
    corp_type_table = table('corp_type',
                                  column('code', String),
                                  column('desc', String),
                                  column('default', Boolean)
                                  )
    # Insert code values
    op.bulk_insert(
        corp_type_table,
        [
            {'code': 'NR', 'desc': 'Names Request', 'default': False}
        ]
    )

def downgrade():
    pass

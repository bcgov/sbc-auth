"""adding_new_business_corp_type

Revision ID: bab2eefb9412
Revises: 4efb2fdcc1ab
Create Date: 2020-05-21 17:25:46.599633

"""
from alembic import op
import sqlalchemy as sa
from alembic import op
import sqlalchemy as sa
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = 'bab2eefb9412'
down_revision = '4efb2fdcc1ab'
branch_labels = None
depends_on = None


def upgrade():
    corp_type_table = table('corp_type',
                               column('code', String),
                               column('desc', String),
                               column('default', Boolean)
                               )
    op.bulk_insert(
        corp_type_table,
        [
            {'code': 'TMP', 'desc': 'New Business', 'default': False},
            {'code': 'BC', 'desc': 'Benefit Company', 'default': False}
        ]
    )


def downgrade():
    pass

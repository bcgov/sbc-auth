"""added director search role

Revision ID: 1786b8de5f43
Revises: 8b49eb83f064
Create Date: 2020-04-03 07:22:44.544017

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '1786b8de5f43'
down_revision = '8b49eb83f064'
branch_labels = None
depends_on = None


def upgrade():
    product_role_code_table = table('product_role_code',
                                    column('id', Integer),
                                    column('code', String),
                                    column('desc', String),
                                    column('product_code', String)
                                    )


    op.bulk_insert(
        product_role_code_table,
        [
            {'id': 3, 'code': 'search', 'desc': 'Search', 'product_code': 'DIR_SEARCH'}
        ]
    )


def downgrade():
    pass

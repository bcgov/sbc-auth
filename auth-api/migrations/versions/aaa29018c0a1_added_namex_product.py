"""added namex product

Revision ID: aaa29018c0a1
Revises: e38ad1ce6d21
Create Date: 2020-12-16 12:11:17.750038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aaa29018c0a1'
down_revision = 'e38ad1ce6d21'
branch_labels = None
depends_on = None


def upgrade():
    product_code_table = sa.sql.table('product_code',
                                      sa.column('code', sa.String),
                                      sa.column('desc', sa.String),
                                      sa.column('default', sa.Boolean),
                                      sa.column('type_code', sa.String)
                                      )

    op.bulk_insert(
        product_code_table,
        [
            {'code': 'NRO', 'desc': 'Names Request', 'default': False, 'type_code': 'INTERNAL'}
        ]
    )

    op.execute("insert into product_subscription (org_id, product_code) "
               "select org_id, 'NRO' FROM product_subscription where product_code='BUSINESS' ")


def downgrade():
    op.execute("DELETE FROM product_subscription WHERE product_code='NRO'")
    op.execute("DELETE FROM product_code WHERE code='NRO'")


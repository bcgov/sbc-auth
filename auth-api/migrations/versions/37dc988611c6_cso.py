"""cso

Revision ID: 37dc988611c6
Revises: 385a6a9ae5a8
Create Date: 2021-09-23 14:57:05.541878

"""
from alembic import op
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '37dc988611c6'
down_revision = '385a6a9ae5a8'
branch_labels = None
depends_on = None


def upgrade():
    # Add master data for product_code and product_role_code
    product_code_table = table('product_codes',
                               column('code', String),
                               column('description', String),
                               column('default', Boolean),
                               column('type_code', String),
                               column('hidden', Boolean),
                               column('linked_product_code', String),
                               column('need_review', Boolean),
                               column('premium_only', Boolean),
                               column('url', String)
                               )
    op.bulk_insert(
        product_code_table,
        [
            {
                'code': 'CSO',
                'description': 'Court Services Online',
                'default': False,
                'type_code': 'PARTNER',
                'hidden': True,
                'linked_product_code': None,
                'need_review': False,
                'premium_only': True,
                'url': ''
            }
        ]
    )


def downgrade():
    op.execute("delete from product_codes where code='CSO'")
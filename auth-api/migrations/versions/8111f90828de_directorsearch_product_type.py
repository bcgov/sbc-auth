"""directorsearch product type

Revision ID: 8111f90828de
Revises: 243d9782085e
Create Date: 2020-02-24 12:59:10.005224

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean, Date

# revision identifiers, used by Alembic.
revision = '8111f90828de'
down_revision = '243d9782085e'
branch_labels = None
depends_on = None


def upgrade():
    product_code_table = table('product_code',
                               column('code', String),
                               column('desc', String),
                               column('default', Boolean)
                               )
    op.bulk_insert(product_code_table,
                   [{'code': "DIR_SEARCH", 'desc': 'Director Search', 'default': False}])

    org_type_table = table('org_type',
                           column('code', String),
                           column('desc', String),
                           column('default', Boolean)
                           )

    op.bulk_insert(org_type_table,
                   [{'code': "PUBLIC", 'desc': 'PUBLIC', 'default': False}])
    op.add_column('org', sa.Column('access_type', sa.String(length=250), nullable=True))
    op.add_column('invitation', sa.Column('invitation_type', sa.String(length=100), nullable=True))


def downgrade():
    op.execute("DELETE FROM product_code WHERE code='DIR_SEARCH'")
    op.execute("DELETE FROM org_type WHERE code='PUBLIC'")
    op.drop_column('org', 'access_type')
    op.drop_column('invitation', 'invitation_type')

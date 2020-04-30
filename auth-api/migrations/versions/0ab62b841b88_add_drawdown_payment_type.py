"""add_drawdown_payment_type

Revision ID: 0ab62b841b88
Revises: b1fb7d214cb7
Create Date: 2020-04-20 19:31:27.260794

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table



# revision identifiers, used by Alembic.
revision = '0ab62b841b88'
down_revision = 'b1fb7d214cb7'
branch_labels = None
depends_on = None


def upgrade():
    # Insert codes and descriptions for payment types
    payment_types_table = table('payment_type',
                               column('code', String),
                               column('desc', String),
                               column('default', Boolean)
                               )
    op.bulk_insert(
        payment_types_table,
        [
            {'code': 'DRAWDOWN', 'desc': 'BC Online Drawdown Payment', 'default': False}
        ]
    )

    org_type_table = table('org_type',
                           column('code', String),
                           column('desc', String),
                           column('default', Boolean)
                           )

    op.bulk_insert(
        org_type_table,
        [
            {'code': 'PREMIUM', 'desc': 'Premium accounts', 'default': False}
        ]
    )


def downgrade():
    op.execute('delete from payment_type where code=\'DRAWDOWN\'')
    op.execute('delete from org_type where code=\'PREMIUM\'')

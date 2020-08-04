"""add direct payment to payment types

Revision ID: 2e58cc00009b
Revises: 32b50299e3a3
Create Date: 2020-08-04 14:59:16.512957

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '2e58cc00009b'
down_revision = '32b50299e3a3'
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
            {'code': 'DIRECT_PAY', 'desc': 'Direct Pay', 'default': False}
        ]
    )


def downgrade():
    op.execute('delete from payment_type where code=\'DIRECT_PAY\'')

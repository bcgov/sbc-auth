"""create payment methods permission

Revision ID: c51a33f55be6
Revises: 18a4955730f9
Create Date: 2020-11-05 16:12:46.942143

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = 'c51a33f55be6'
down_revision = '18a4955730f9'
branch_labels = None
depends_on = None


def upgrade():
    permissions_table = table('permissions',
                              column('id', sa.Integer()),
                              column('membership_type_code', sa.String(length=15)),
                              column('actions', sa.String(length=100)))

    # Insert code values
    op.bulk_insert(
        permissions_table,
        [
            {'id': 24, 'membership_type_code': 'ADMIN', 'actions': 'VIEW_PAYMENT_METHODS'},
        ]
    )


def downgrade():
    op.execute('delete from permissions where id=24')

"""create statement permissions

Revision ID: 032248a1b370
Revises: 5cf63f567a62
Create Date: 2020-09-04 16:22:05.235285

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '032248a1b370'
down_revision = '5cf63f567a62'
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
            {'id': 20, 'membership_type_code': 'ADMIN', 'actions': 'MANAGE_STATEMENTS'},
            {'id': 21, 'membership_type_code': 'COORDINATOR', 'actions': 'MANAGE_STATEMENTS'},
        ]
    )


def downgrade():
    op.execute('delete from permissions where id=20')
    op.execute('delete from permissions where id=21')

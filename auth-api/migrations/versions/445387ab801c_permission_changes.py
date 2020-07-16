"""permission_changes

Revision ID: 445387ab801c
Revises: f1ce3f279b60
Create Date: 2020-07-14 14:34:15.133224

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '445387ab801c'
down_revision = 'f1ce3f279b60'
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
            {'id': 13, 'membership_type_code': 'USER', 'actions': 'VIEW_ACCOUNT'}
        ]
    )


def downgrade():
    op.execute('delete from permissions where id=13')

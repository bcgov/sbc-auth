"""deactivate_permissions

Revision ID: 3b485a23d057
Revises: c44fff21c830
Create Date: 2021-06-25 13:51:45.984079

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '3b485a23d057'
down_revision = 'c44fff21c830'
branch_labels = None
depends_on = None


def upgrade():
    permissions_table = table('permissions',
                              column('membership_type_code', sa.String(length=15)),
                              column('org_status_code', sa.String(length=25)),
                              column('actions', sa.String(length=100)))
    op.execute('delete from permissions where actions=\'deactivate_account\'')
    op.execute('select setval(\'permissions_id_seq\', 78, true);')  # No need to include this next time onwards
    op.bulk_insert(
        permissions_table,
        [
            {'membership_type_code': 'ADMIN', 'org_status_code': None, 'actions': 'deactivate_account'}
        ]
    )


def downgrade():
    op.execute("delete from permissions where actions='deactivate_account'")

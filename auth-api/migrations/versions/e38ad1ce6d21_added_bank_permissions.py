"""added bank permissions

Revision ID: e38ad1ce6d21
Revises: 316ae45f54bc
Create Date: 2020-12-10 06:51:09.927372

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = 'e38ad1ce6d21'
down_revision = '316ae45f54bc'
branch_labels = None
depends_on = None


def upgrade():
    permissions_table = table('permissions',
                              column('id', sa.Integer()),
                              column('membership_type_code', sa.String(length=15)),
                              column('org_status_code', sa.String(length=25)),
                              column('actions', sa.String(length=100)))

    # Insert code values
    op.bulk_insert(
        permissions_table,
        [
            {'id': 55, 'membership_type_code': 'ADMIN', 'org_status_code': None,
             'actions': 'manage_bank_info'},
            {'id': 56, 'membership_type_code': 'ADMIN', 'org_status_code': None,
             'actions': 'view_bank_account_number'},
            {'id': 57, 'membership_type_code': 'ADMIN', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'manage_bank_info'},
            {'id': 58, 'membership_type_code': 'ADMIN', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'view_bank_account_number'},
        ]
    )
    # Update actions to lower case


def downgrade():
    op.execute('delete from permissions where id between 55 and 58')

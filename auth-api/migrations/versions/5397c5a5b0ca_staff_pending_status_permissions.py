"""staff_pending_status_permissions

Revision ID: 5397c5a5b0ca
Revises: 3b485a23d057
Create Date: 2021-06-28 10:24:51.991657

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '5397c5a5b0ca'
down_revision = '3b485a23d057'
branch_labels = None
depends_on = None


def upgrade():
    permissions_table = table('permissions',
                              column('id', sa.Integer()),
                              column('membership_type_code', sa.String(length=15)),
                              column('org_status_code', sa.String(length=25)),
                              column('actions', sa.String(length=100)))
    conn = op.get_bind()
    res = conn.execute(
        f"select max(id) from permissions;")
    latest_id = res.fetchall()[0][0]
    op.bulk_insert(
        permissions_table,
        [
            {'id': latest_id + 1, 'membership_type_code': 'ADMIN', 'org_status_code': 'PENDING_STAFF_REVIEW',
             'actions': 'view'}
        ]
    )


def downgrade():
    op.execute(
        "delete from permissions where membership_type_code='ADMIN' and org_status_code='PENDING_STAFF_REVIEW' "
        "and actions='view'")

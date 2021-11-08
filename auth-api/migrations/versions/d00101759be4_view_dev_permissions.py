"""view dev permissions

Revision ID: d00101759be4
Revises: 2468d14cc44c
Create Date: 2021-11-08 09:17:15.666605

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = 'd00101759be4'
down_revision = '2468d14cc44c'
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

    # Insert code values
    op.bulk_insert(
        permissions_table,
        [
            {'id': latest_id + 1, 'membership_type_code': 'ADMIN', 'org_status_code': None,
             'actions': 'VIEW_DEVELOPER_ACCESS'}
        ]
    )


def downgrade():
    op.execute('delete from permissions where action="VIEW_DEVELOPER_ACCESS"')

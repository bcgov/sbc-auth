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
    permissions_table = table('permissions', column('membership_type_code', sa.String(length=15)), column('actions',
                                                                                                          sa.String(
                                                                                                              length=100)))  #
    op.bulk_insert(permissions_table, [{'membership_type_code': 'ADMIN', 'actions': 'VIEW_DEVELOPER_ACCESS'}])


def downgrade():
    op.execute('delete from permissions where actions="VIEW_DEVELOPER_ACCESS"')

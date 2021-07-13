"""edit business permissions

Revision ID: eb771b2012b7
Revises: 9e4305679a5d
Create Date: 2021-07-12 00:26:42.228008

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = 'eb771b2012b7'
down_revision = '9e4305679a5d'
branch_labels = None
depends_on = None

def upgrade():
    permissions_table = table('permissions',
                              column('membership_type_code', sa.String(length=15)),
                              column('org_status_code', sa.String(length=25)),
                              column('actions', sa.String(length=100)))
    op.bulk_insert(
        permissions_table,
        [
            {'membership_type_code': 'ADMIN', 'org_status_code': None, 'actions': 'EDIT_BUSINESS_INFO'}
        ]
    )


def downgrade():
    op.execute("delete from permissions where actions='EDIT_BUSINESS_INFO'")


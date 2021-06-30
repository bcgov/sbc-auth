"""view_teammember_auth

Revision ID: f55e4cc1aaaa
Revises: 5397c5a5b0ca
Create Date: 2021-06-29 07:58:31.514016

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = 'f55e4cc1aaaa'
down_revision = '5397c5a5b0ca'
branch_labels = None
depends_on = None


def upgrade():
    permissions_table = table('permissions',
                              column('id', sa.Integer()),
                              column('membership_type_code', sa.String(length=15)),
                              column('org_status_code', sa.String(length=25)),
                              column('actions', sa.String(length=100)))
    op.bulk_insert(
        permissions_table,
        [
            {'membership_type_code': 'ADMIN', 'org_status_code': '',
             'actions': 'view_user_loginsource'}
        ]
    )


def downgrade():
    op.execute(
        "delete from permissions where membership_type_code='ADMIN' and actions='view_user_loginsource'")


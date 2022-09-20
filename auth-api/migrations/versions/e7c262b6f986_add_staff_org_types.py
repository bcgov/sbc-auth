"""Add org types for staff and sbc-staff.

Revision ID: e7c262b6f986
Revises: c6e4754d28cf
Create Date: 2022-09-07 13:58:56.639360

"""
from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = 'e7c262b6f986'
down_revision = 'c6e4754d28cf'
branch_labels = None
depends_on = None


def upgrade():
    org_type_table = table('org_types',
                        column('code', String),
                        column('desc', String),
                        column('default', Boolean)
                    )

    op.bulk_insert(
        org_type_table,
        [
            {'code': 'STAFF', 'desc': 'BC Registries Staff', 'default': False},
            {'code': 'SBC_STAFF', 'desc': 'Service BC Staff', 'default': False},
        ]
    )


def downgrade():
    op.execute('delete from org_type where code=\'STAFF\'')
    op.execute('delete from org_type where code=\'SBC_STAFF\'')

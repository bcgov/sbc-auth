"""Add org types for read-only staff.

Revision ID: 7f48833011c3
Revises: 63cfd9b160d7
Create Date: 2025-02-19 15:54:22.459049

"""
from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '7f48833011c3'
down_revision = '63cfd9b160d7'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('org_types', 'code', type_=String(30))

    org_type_table = table('org_types',
                        column('code', String),
                        column('description', String),
                        column('default', Boolean)
                    )

    op.bulk_insert(
        org_type_table,
        [
            {'code': 'MAXIMUS_STAFF', 'description': 'Maximus Staff', 'default': False},
            {'code': 'CONTACT_CENTRE_STAFF', 'description': 'Contact Centre Staff', 'default': False},
        ]
    )


def downgrade():
    op.execute('delete from org_types where code=\'MAXIMUS_STAFF\'')
    op.execute('delete from org_types where code=\'CONTACT_CENTRE_STAFF\'')

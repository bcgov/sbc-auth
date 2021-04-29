"""affidavit inactive status added

Revision ID: a37f90e6802d
Revises: d0392ebda924
Create Date: 2021-04-28 12:26:09.064247

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = 'a37f90e6802d'
down_revision = 'd0392ebda924'
branch_labels = None
depends_on = None


def upgrade():
    # Insert affidavit statuses

    affidavit_status_table = table('affidavit_statuses',
                             column('code', String),
                             column('description', String),
                             column('default', Boolean))
    op.bulk_insert(
        affidavit_status_table,
        [
            {'code': 'INACTIVE', 'description': 'Inactivated affidavit', 'default': False}
        ]
    )

def downgrade():
    op.execute('delete from affidavit_statuses where code=\'INACTIVE\'')

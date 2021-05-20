"""suspended status 

Revision ID: 8260fac9943d
Revises: b23a04d2e331
Create Date: 2021-02-08 10:41:23.530382

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '8260fac9943d'
down_revision = 'b23a04d2e331'
branch_labels = None
depends_on = None


def upgrade():
    # Insert codes and descriptions for organization status
    org_status_table = table('org_statuses',
                             column('code', String),
                             column('description', String),
                             column('default', Boolean)
                             )
    op.bulk_insert(
        org_status_table,
        [
            {'code': 'SUSPENDED', 'description': 'Status for an org which is suspended.',
             'default': False}
        ]
    )


def downgrade():
    op.execute('delete from org_statuses where code=\'SUSPENDED\'')


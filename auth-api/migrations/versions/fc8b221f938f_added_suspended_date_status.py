"""Added suspended date,status

Revision ID: fc8b221f938f
Revises: c51a33f55be6
Create Date: 2020-11-22 15:32:40.287363

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = 'fc8b221f938f'
down_revision = 'c51a33f55be6'
branch_labels = None
depends_on = None


def upgrade():
    # Insert codes and descriptions for organization status
    org_status_table = table('org_status',
                             column('code', String),
                             column('desc', String),
                             column('default', Boolean)
                             )
    op.bulk_insert(
        org_status_table,
        [
            {'code': 'NSF_SUSPENDED', 'desc': 'Status for an org which caused Non Sufficient fund for payment.',
             'default': False}
        ]
    )
    op.add_column('org', sa.Column('suspended_on', sa.DateTime(), nullable=True))
    op.add_column('org_version', sa.Column('suspended_on', sa.DateTime(), autoincrement=False, nullable=True))


def downgrade():
    op.execute('delete from org_status where code=\'NSF_SUSPENDED\'')
    op.drop_column('org', 'suspended_on')
    op.drop_column('org_version', 'suspended_on')

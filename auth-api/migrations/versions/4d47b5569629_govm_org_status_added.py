"""govm org status added

Revision ID: 4d47b5569629
Revises: 4c6ca48245be
Create Date: 2021-03-09 07:02:28.920945

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table
from sqlalchemy import Boolean, String

# revision identifiers, used by Alembic.
revision = '4d47b5569629'
down_revision = '4c6ca48245be'
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
            {'code': 'PENDING_INVITE_ACCEPT', 'description': 'User invited to his account.Waiting user action',
             'default': False},
            {'code': 'PENDING_STAFF_REVIEW', 'description': 'Waiting for staff review for user',
             'default': False}
        ]
    )


def downgrade():
    op.execute("delete from org_statuses where code in ('PENDING_INVITE_ACCEPT','PENDING_STAFF_REVIEW')")

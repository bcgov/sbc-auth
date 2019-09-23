"""empty message

Revision ID: 4a305e1c8c69
Revises: 6848a30e95cd
Create Date: 2019-09-23 10:05:27.159104

"""
from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '4a305e1c8c69'
down_revision = '6848a30e95cd'
branch_labels = None
depends_on = None


def upgrade():
    # Insert 'Failed' Status for the Invitation
    invitation_status_table = table('invitation_status',
                                    column('code', String),
                                    column('desc', String),
                                    column('default', Boolean)
                                    )
    op.bulk_insert(
        invitation_status_table,
        [
            {'code': 'FAILED', 'desc': 'Failed state of the invitation', 'default': True}
        ]
    )


def downgrade():
    op.execute('TRUNCATE TABLE invitation_status CASCADE;')

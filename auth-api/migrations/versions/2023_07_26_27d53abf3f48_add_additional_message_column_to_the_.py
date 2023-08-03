"""Add 'additional message' column to the Affiliation invitation table.

Revision ID: 27d53abf3f48
Revises: b20a33cb84f2
Create Date: 2023-07-26 15:47:32.875016

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table, String, Boolean

# revision identifiers, used by Alembic.
revision = '27d53abf3f48'
down_revision = 'b20a33cb84f2'
branch_labels = None
depends_on = None


def upgrade():
    ait = table('affiliation_invitation_types',
                column('code', String),
                column('description', String),
                column('default', Boolean)
                )
    op.bulk_insert(ait,
                   [
                       {'code': 'REQUEST', 'description': 'An affiliation invitation initiated through Request Access flow on business search modal', 'default': False}
                   ])

    op.add_column('affiliation_invitations', sa.Column('additional_message', sa.String(length=4000), nullable=True))


def downgrade():
    op.drop_column('affiliation_invitations', 'additional_message')
    op.execute("DELETE FROM affiliation_invitation_types WHERE code = 'REQUEST'")

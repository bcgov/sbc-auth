"""affiliation_invitations_to_org_nullable

Revision ID: 628b52a95bad
Revises: 27d53abf3f48
Create Date: 2023-08-08 11:12:40.149008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '628b52a95bad'
down_revision = '18823fc88aac'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('affiliation_invitations', 'to_org_id',
                    nullable=True)
    op.alter_column('affiliation_invitations', 'recipient_email',
                    nullable=True)


def downgrade():
    op.alter_column('affiliation_invitations', 'to_org_id',
                    nullable=False)
    op.alter_column('affiliation_invitations', 'recipient_email',
                    nullable=False)

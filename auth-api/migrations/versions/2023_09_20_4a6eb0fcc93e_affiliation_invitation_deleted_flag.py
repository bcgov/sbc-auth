"""affiliation invitation deleted flag

Revision ID: 4a6eb0fcc93e
Revises: 98bee9969323
Create Date: 2023-09-20 10:32:24.804185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a6eb0fcc93e'
down_revision = '98bee9969323'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('affiliation_invitations', sa.Column('is_deleted', sa.Boolean(), nullable=False,
                                                       server_default=sa.false()))


def downgrade():
    op.drop_column('affiliation_invitations', 'is_deleted')

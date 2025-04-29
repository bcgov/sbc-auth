"""Drop the environment column no longer needed

Revision ID: 3a1b9e52d7d8
Revises: bddf9fe7468c
Create Date: 2025-04-29 09:50:56.838619

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3a1b9e52d7d8'
down_revision = 'bddf9fe7468c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('affiliations', schema=None) as batch_op:
        batch_op.drop_index('ix_affiliations_environment')
        batch_op.drop_column('environment')

    with op.batch_alter_table('affiliations_history', schema=None) as batch_op:
        batch_op.drop_index('ix_affiliations_history_environment')
        batch_op.drop_column('environment')


def downgrade():
    with op.batch_alter_table('affiliations_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('environment', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
        batch_op.create_index('ix_affiliations_history_environment', ['environment'], unique=False)

    with op.batch_alter_table('affiliations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('environment', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
        batch_op.create_index('ix_affiliations_environment', ['environment'], unique=False)

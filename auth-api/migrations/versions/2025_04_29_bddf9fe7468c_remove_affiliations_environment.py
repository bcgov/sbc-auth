"""Clear out the sandbox affiliations

Revision ID: bddf9fe7468c
Revises: 0879befaf0b6
Create Date: 2025-04-29 09:49:31.783306

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bddf9fe7468c'
down_revision = '0879befaf0b6'
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

    
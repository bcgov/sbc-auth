"""add bcol_account_name to org

Revision ID: dfd28e2b34a3
Revises: 5f51253eeced
Create Date: 2021-01-21 13:33:36.454377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfd28e2b34a3'
down_revision = '5f51253eeced'
branch_labels = None
depends_on = None


def upgrade():
    # Add new column to save original BCOL account name for account linked to BCOL account
    op.add_column('org', sa.Column('bcol_account_name', sa.String(length=250), nullable=True))
    op.add_column('org_version', sa.Column('bcol_account_name', sa.String(length=250), autoincrement=False, nullable=True))

    # Set BCOL account name to name for existing account who already linked to BCOL account
    op.execute("UPDATE org SET bcol_account_name=name WHERE bcol_account_id is not null;")


def downgrade():
    op.drop_column('org', 'bcol_account_name')
    op.drop_column('org_version', 'bcol_account_name')

"""Add in index for affiliation.org_id

Revision ID: dfe9614f7fb0
Revises: b21908e1893f
Create Date: 2026-03-12 11:41:33.351253

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dfe9614f7fb0'
down_revision = 'b21908e1893f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('affiliations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_affiliations_org_id'), ['org_id'], unique=False)

    with op.batch_alter_table('affiliations_history', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_affiliations_history_org_id'), ['org_id'], unique=False)


def downgrade():
    with op.batch_alter_table('affiliations_history', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_affiliations_history_org_id'))

    with op.batch_alter_table('affiliations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_affiliations_org_id'))

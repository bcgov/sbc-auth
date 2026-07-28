"""add_org_redirect_urls_table

Revision ID: bff7f0c3bac4
Revises: 1da47e33dc8f
Create Date: 2026-07-03 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bff7f0c3bac4'
down_revision = '1da47e33dc8f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('org_redirect_urls',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=False,
              comment='Vendor org that owns this redirect URL'),
    sa.Column('redirect_url', sa.String(length=2048), nullable=False,
              comment='Full URL to which BCROS may redirect after linking; must be https'),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('modified_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['org_id'], ['orgs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('org_redirect_urls', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_org_redirect_urls_org_id'), ['org_id'], unique=False)


def downgrade():
    with op.batch_alter_table('org_redirect_urls', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_org_redirect_urls_org_id'))
    op.drop_table('org_redirect_urls')

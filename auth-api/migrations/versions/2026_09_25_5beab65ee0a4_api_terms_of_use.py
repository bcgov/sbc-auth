"""API Terms of Use per-org acceptance table.

Revision ID: 5beab65ee0a4
Revises: bb7f11e0e414
Create Date: 2026-09-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5beab65ee0a4'
down_revision = 'bb7f11e0e414'
branch_labels = None
depends_on = None

# API Terms documents (type 'termsofuse_api') are published by their own data migration, one per version.
# documents.version_id is the primary key across all document types and the latest version is picked by
# sorting version_id as text, using 'k' prefix and zero-padded version (eg k01, k02, etc.)
# Published versions should not be updated or deleted, because org_api_terms_acceptances references them.


def upgrade():
    op.create_table('org_api_terms_acceptances',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=False,
              comment='Org that accepted the API Terms of Use'),
    sa.Column('version_id', sa.String(length=10), nullable=False,
              comment='Version of the termsofuse_api document that was accepted'),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('modified_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['org_id'], ['orgs.id'], ),
    sa.ForeignKeyConstraint(['version_id'], ['documents.version_id'], ),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('org_id', 'version_id', name='uq_org_api_terms_org_version')
    )
    op.create_index(op.f('ix_org_api_terms_acceptances_org_id'), 'org_api_terms_acceptances', ['org_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_org_api_terms_acceptances_org_id'), table_name='org_api_terms_acceptances')
    op.drop_table('org_api_terms_acceptances')

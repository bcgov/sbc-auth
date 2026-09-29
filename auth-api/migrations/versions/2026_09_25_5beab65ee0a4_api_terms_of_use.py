"""API Terms of Use document and per-org acceptance.

Revision ID: 5beab65ee0a4
Revises: bb7f11e0e414
Create Date: 2026-09-25 00:00:00.000000

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy import DateTime, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '5beab65ee0a4'
down_revision = 'bb7f11e0e414'
branch_labels = None
depends_on = None

# documents.version_id is the primary key across all document types,
# so API terms versions need an id no other type uses. The latest version is picked by sorting
# version_id as text, so keep the 'k' prefix and zero-padded width: k01, k02, ... k99.
# 'created' isn't used to pick the latest version, but set it where possible to record when a version was published.
API_TERMS_VERSION = 'k01'
API_TERMS_TYPE = 'termsofuse_api'


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

    documents = table('documents',
                      column('version_id', String),
                      column('type', String),
                      column('content_type', String),
                      column('content', String),
                      column('created', DateTime))
    html_content = """
      <p>
        [Placeholder]
      </p>
    """
    now = datetime.now()
    op.bulk_insert(
        documents,
        [
            {'version_id': API_TERMS_VERSION, 'type': API_TERMS_TYPE, 'content_type': 'text/html',
             'content': html_content, 'created': now}
        ]
    )

    # Orgs that already have API access accepted the terms when their keys were issued,
    # so record them as accepted. A NULL created_by_id marks these backfilled rows.
    op.get_bind().execute(
        sa.text(
            "INSERT INTO org_api_terms_acceptances (org_id, version_id, created, modified) "
            "SELECT id, :version_id, :now, :now FROM orgs WHERE has_api_access = true"
        ),
        {'version_id': API_TERMS_VERSION, 'now': now}
    )


def downgrade():
    op.drop_index(op.f('ix_org_api_terms_acceptances_org_id'), table_name='org_api_terms_acceptances')
    op.drop_table('org_api_terms_acceptances')
    op.execute(f"DELETE FROM documents WHERE type = '{API_TERMS_TYPE}'")

"""added content type to docs

Revision ID: 422daf97fd19
Revises: 598dd27fc660
Create Date: 2020-06-09 07:58:20.103049

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table
from sqlalchemy import Integer, String

# revision identifiers, used by Alembic.
revision = '422daf97fd19'
down_revision = '598dd27fc660'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('documents', sa.Column('content_type', sa.String(length=50), nullable=True))
    op.execute("update documents set content_type='text/html'")

    documents = table('documents',
                      column('version_id', String),
                      column('type', String),
                      column('content', String),
                      column('content_type', String))

    file_name = "affidavit_v1.pdf"
    op.bulk_insert(
        documents,
        [
            {'version_id': 'a1', 'type': 'affidavit', 'content': file_name, 'content_type': 'application/pdf'}
        ]
    )
    

def downgrade():
    op.execute("DELETE FROM DOCUMENTS WHERE version_id='a1'")
    op.drop_column('documents', 'content_type')

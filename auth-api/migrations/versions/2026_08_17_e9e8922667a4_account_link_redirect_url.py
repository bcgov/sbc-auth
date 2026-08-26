""" Add redirect_url to account_linking_keys for parameter traceability at the time of key generation.

Revision ID: e9e8922667a4
Revises: bff7f0c3bac4
Create Date: 2026-08-17 07:42:20.441828

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e9e8922667a4'
down_revision = 'bff7f0c3bac4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('account_linking_keys', schema=None) as batch_op:
        batch_op.add_column(sa.Column('redirect_url', sa.String(length=2048), nullable=True, comment="Redirect URL validated against the vendor account's registered redirect URLs at generation time"))
        
def downgrade():
    with op.batch_alter_table('account_linking_keys', schema=None) as batch_op:
        batch_op.drop_column('redirect_url')

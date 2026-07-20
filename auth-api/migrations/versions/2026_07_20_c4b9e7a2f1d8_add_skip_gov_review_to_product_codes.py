"""Add skip_gov_review flag to product_codes and enable it for BCA.

Revision ID: c4b9e7a2f1d8
Revises: dfe9614f7fb0
Create Date: 2026-07-20 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c4b9e7a2f1d8'
down_revision = 'dfe9614f7fb0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('product_codes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('skip_gov_review', sa.Boolean(), nullable=True))

    op.execute("update product_codes set skip_gov_review=false where skip_gov_review is null")
    op.execute("update product_codes set skip_gov_review=true where code='BCA'")


def downgrade():
    with op.batch_alter_table('product_codes', schema=None) as batch_op:
        batch_op.drop_column('skip_gov_review')

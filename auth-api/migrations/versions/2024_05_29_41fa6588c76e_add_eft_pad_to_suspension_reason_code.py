"""Add EFT PAD to suspension_reason_code

Revision ID: 41fa6588c76e
Revises: 1e4b6359f470
Create Date: 2024-05-29 10:36:53.016963

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41fa6588c76e'
down_revision = '1e4b6359f470'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO suspension_reason_codes "
            "(code, description,\"default\") "
            "VALUES "
            "('EFT', 'Electronic Funds Transfer', false)")
    op.execute("INSERT INTO suspension_reason_codes "
            "(code, description,\"default\") "
            "VALUES "
            "('PAD', 'Pre-Authorized Debit', false)")


def downgrade():
    op.execute("DELETE FROM suspension_reason_codes WHERE code in ('EFT', 'PAD')")

"""remove EFT_NSF from suspension_reason_codes

Revision ID: acc7e2e2c2d7
Revises: 7bf8428e568e
Create Date: 2024-06-24 12:41:33.684863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acc7e2e2c2d7'
down_revision = '7bf8428e568e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM suspension_reason_codes WHERE code = 'EFT_NSF'")


def downgrade():
    op.execute("INSERT INTO suspension_reason_codes "
        "(code, description,\"default\") "
        "VALUES "
        "('EFT_NSF', 'EFT NSF', false)")

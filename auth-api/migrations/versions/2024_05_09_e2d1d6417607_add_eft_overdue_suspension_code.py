"""empty message

Revision ID: e2d1d6417607
Revises: 17369fa9416d
Create Date: 2024-05-09 15:39:36.678009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2d1d6417607'
down_revision = '17369fa9416d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO suspension_reason_codes "
            "(code, description,\"default\") "
            "VALUES "
            "('OVERDUE_EFT', 'Overdue EFT Payments', false)")


def downgrade():
    op.execute("DELETE FROM suspension_reason_codes WHERE code in ('OVERDUE_EFT')")

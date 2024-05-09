"""Add Overdue EFT Payments suspension code

Revision ID: a8c61064e6fd
Revises: e65cc8ab51cc
Create Date: 2024-05-07 15:53:21.674906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8c61064e6fd'
down_revision = 'e65cc8ab51cc'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO suspension_reason_codes "
            "(code, description,\"default\") "
            "VALUES "
            "('OVERDUE_EFT', 'Overdue EFT Payments', false)")
    op.execute("commit")


def downgrade():
    op.execute("DELETE FROM suspension_reason_codes WHERE code in ('OVERDUE_EFT')")
    op.execute("commit")

"""Unhide BCA product on Products and Payment page.

Revision ID: bb7f11e0e414
Revises: a3f5c8e2b1d7
Create Date: 2026-09-08 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "bb7f11e0e414"
down_revision = "a3f5c8e2b1d7"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE product_codes SET hidden=false WHERE code='BCA'")


def downgrade():
    op.execute("UPDATE product_codes SET hidden=true WHERE code='BCA'")

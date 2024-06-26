"""Add in new products for BCFMS, BCRHP 

Revision ID: af98933abe93
Revises: acc7e2e2c2d7
Create Date: 2024-06-26 14:46:57.699068

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af98933abe93'
down_revision = 'acc7e2e2c2d7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO product_codes "
               "(code, description,\"default\", type_code, hidden, need_review, need_system_admin, premium_only, url) "
               "VALUES "
               "('BCFMS', 'BC Fossil Management System', false, 'PARTNER', true, false, false, false,'')")
    op.execute("INSERT INTO product_codes "
               "(code, description,\"default\", type_code, hidden, need_review, need_system_admin, premium_only, url) "
               "VALUES "
               "('BCRHP', 'BC Register of Historic Places', false, 'PARTNER', true, false, false, false,'')")

def downgrade():
    op.execute("DELETE FROM product_codes WHERE code in ('BCFMS', 'BCRHP')")

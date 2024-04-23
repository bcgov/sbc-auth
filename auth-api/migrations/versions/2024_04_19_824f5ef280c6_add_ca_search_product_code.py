"""add_ca_search_product_code

Revision ID: 824f5ef280c6
Revises: e65cc8ab51cc
Create Date: 2024-04-19 15:02:21.899101

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '824f5ef280c6'
down_revision = 'e65cc8ab51cc'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO public.product_codes "
             "(code, description,\"default\", type_code, hidden, need_review, need_system_admin, premium_only, url) "
             "VALUES "
             "('CA_SEARCH', 'Competent Authority Search', false, 'INTERNAL', true, false, true, false,'')")
    op.execute("commit")

def downgrade():
    op.execute("DELETE FROM product_codes WHERE code in ('CA_SEARCH')")
    op.execute("commit")

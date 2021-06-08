"""restricted ppr

Revision ID: e7f46c30d356
Revises: 9b04140db7d3
Create Date: 2021-06-03 10:40:35.754106

"""

# revision identifiers, used by Alembic.
from alembic import op

revision = 'e7f46c30d356'
down_revision = '9b04140db7d3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO public.product_codes "
               "(code, description,\"default\", type_code, hidden, need_review, premium_only, url) "
               "VALUES "
               "('RPPR', 'Restricted Personal Property Registry',false, 'INTERNAL', true,false, true, "
               "'https://www.bcregistry.ca/ppr')")
    op.execute("commit")


def downgrade():
    op.execute("DELETE FROM product_codes WHERE code in ('RPPR')")

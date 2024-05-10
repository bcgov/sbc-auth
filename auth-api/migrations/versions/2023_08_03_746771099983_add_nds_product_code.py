"""add_NDS_product_code

Revision ID: 746771099983
Revises: b20a33cb84f2
Create Date: 2023-08-03 16:07:51.025459

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '746771099983'
down_revision = 'b20a33cb84f2'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO product_codes "
             "(code, description,\"default\", type_code, hidden, need_review, premium_only, url) "
             "VALUES "
             "('NDS', 'New Director Search', false, 'INTERNAL', true, true, false,'')")


def downgrade():
    op.execute("DELETE FROM product_codes WHERE code in ('NDS')")

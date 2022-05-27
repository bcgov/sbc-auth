"""Insert Business search product code

Revision ID: 211deb552319
Revises: da0ce563c18a
Create Date: 2022-05-27 11:43:03.530212

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '211deb552319'
down_revision = 'da0ce563c18a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO public.product_codes "
             "(code, description,\"default\", type_code, hidden, need_review, premium_only, url) "
             "VALUES "
             "('BUSINESS_SEARCH', 'Business Search', false, 'INTERNAL', false, false, true, "
             "'https://www.bcregistry.ca/business/search')")
    op.execute("commit")


def downgrade():
    op.execute("DELETE FROM product_codes WHERE code in ('BUSINESS_SEARCH')")

"""Add MHR product code.

Revision ID: 975fe0b2c859
Revises: 211deb552319
Create Date: 2022-06-02 15:37:13.873620

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '975fe0b2c859'
down_revision = '211deb552319'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO product_codes "
             "(code, description,\"default\", type_code, hidden, need_review, premium_only, url) "
             "VALUES "
             "('MHR', 'Manufactured Home Registry', false, 'INTERNAL', true, false, true, "
             "'https://www.bcregistry.ca/ppr')")



def downgrade():
    op.execute("DELETE FROM product_codes WHERE code in ('MHR')")

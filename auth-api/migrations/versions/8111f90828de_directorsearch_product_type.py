"""directorsearch product type

Revision ID: 8111f90828de
Revises: 243d9782085e
Create Date: 2020-02-24 12:59:10.005224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8111f90828de'
down_revision = '243d9782085e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO product_code (code, \"desc\", \"default\") values ('DIR_SEARCH', 'Director Search', false)")

def downgrade():
    op.execute("DELETE FROM product_code WHERE code='DIR_SEARCH'")

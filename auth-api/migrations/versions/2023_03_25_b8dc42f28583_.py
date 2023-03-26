"""Add in keycloak_group into product codes.

Revision ID: b8dc42f28583
Revises: 501d1179b2f0
Create Date: 2023-03-25 01:20:37.334504

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8dc42f28583'
down_revision = '501d1179b2f0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('product_codes', sa.Column('keycloak_group', sa.String(length=100), nullable=True))
    op.execute("update product_codes set keycloak_group = 'ppr_user' where code = 'PPR';")
    op.execute("update product_codes set keycloak_group = 'mhr_search_user' where code = 'MHR';")
    

def downgrade():
    op.drop_column('product_codes', 'keycloak_group')

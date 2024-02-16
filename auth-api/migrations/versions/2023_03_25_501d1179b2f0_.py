"""Add in keycloak_group into product codes.

Revision ID: 501d1179b2f0
Revises: 7e3f009cb4ae
Create Date: 2023-03-25 01:20:37.334504

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '501d1179b2f0'
down_revision = '7e3f009cb4ae'

branch_labels = None
depends_on = None


def upgrade():
    op.add_column('product_codes', sa.Column('keycloak_group', sa.String(length=100), nullable=True))
    op.execute("update product_codes set keycloak_group = 'ppr_user' where code = 'PPR';")
    op.execute("update product_codes set keycloak_group = 'mhr_search_user' where code = 'MHR';")
    # An alternative could be setting the transaction_per_migration option in run_migrations_online to True.
    # Otherwise the next migration b8dc42f28583 hangs.
    op.execute('COMMIT')

def downgrade():
    op.drop_column('product_codes', 'keycloak_group')

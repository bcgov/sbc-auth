"""Retroactively fix Groups for orgs that have access to PPR / MHR

Revision ID: 6fdb1aeed68d
Revises: b8dc42f28583
Create Date: 2023-03-26 09:12:17.295671

"""
from alembic import op
import sqlalchemy as sa

from auth_api.services.products import Product as ProductService


# revision identifiers, used by Alembic.
revision = '6fdb1aeed68d'
down_revision = 'b8dc42f28583'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    org_res = conn.execute(
        "select distinct org_id from product_subscriptions where product_code in ('MHR','PPR');"
    )
    orgs = org_res.fetchall()
    for org_id in orgs:
        print('Updating keycloak groups for: ', org_id[0])
        ProductService.update_org_product_keycloak_groups(org_id[0])

def downgrade():
    pass

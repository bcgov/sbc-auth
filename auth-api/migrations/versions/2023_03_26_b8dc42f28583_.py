"""Retroactively fix Groups for orgs that have access to PPR / MHR

Revision ID: b8dc42f28583
Revises: 501d1179b2f0
Create Date: 2023-03-26 09:12:17.295671

"""
from alembic import op
import sqlalchemy as sa
from flask import current_app
from auth_api.models import db
from auth_api.services.rest_service import RestService

from auth_api.services.products import Product as ProductService


# revision identifiers, used by Alembic.
revision = 'b8dc42f28583'
down_revision = '501d1179b2f0'
branch_labels = None
depends_on = None


def upgrade():   
    conn = op.get_bind()
    org_res = conn.execute(
        "select distinct org_id from product_subscriptions where product_code in ('MHR','PPR');"
    )
    print('Updating keycloak groups retroactively.')
    orgs = org_res.fetchall()
    for org_id in orgs:
        print('Updating keycloak groups for: ', org_id[0])
        try: 
            ProductService.update_org_product_keycloak_groups(org_id[0])
        except Exception as exc:
            print('Error updating keycloak groups for org: ', org_id[0])
            print(exc)
    print('Finished updating keycloak groups retroactively.')

def downgrade():
    pass

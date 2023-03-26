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
        # Add in products for MHR / PPR.
    conn = op.get_bind()
    org_res = conn.execute(
        "select o.id, o.bcol_user_id from orgs o where bcol_user_id is not null and bcol_account_id is not null and status_code in ('ACTIVE', 'PENDING_STAFF_REVIEW');"
    )
    orgs = org_res.fetchall()
    print('starting migration for BCOL products')
    if len(orgs) > 0:
        token = RestService.get_service_account_token()
    for org_id in orgs:
        try:
            print('Getting bcol profile for ', org_id[0], org_id[1])
            bcol_response = RestService.get(endpoint=current_app.config.get('BCOL_API_URL') + f'/profiles/{org_id[1]}',
                                            token=token)
            print('BCOL Response', bcol_response.json())
            added_subscriptions = ProductService.create_subscription_from_bcol_profile(org_id[0], bcol_response.json().get('profileFlags'))
            if added_subscriptions:
                try: 
                    ProductService.update_org_product_keycloak_groups(org_id[0])
                except Exception as exc:
                    print('Error adding user to group')
                    print(exc)
        except Exception as exc:
            print('Profile Error')
            print(exc)
            raise exc
    db.session.commit()
    
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

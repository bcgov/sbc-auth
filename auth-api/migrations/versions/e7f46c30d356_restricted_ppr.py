"""restricted ppr

Revision ID: e7f46c30d356
Revises: 9b04140db7d3
Create Date: 2021-06-03 10:40:35.754106

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from alembic import op
from flask import current_app

from auth_api.models import db
from auth_api.services.products import Product
from auth_api.services.rest_service import RestService

revision = 'e7f46c30d356'
down_revision = '9b04140db7d3'
branch_labels = None
depends_on = None


def upgrade():
    product_code_table = sa.sql.table('product_codes',
                                      sa.column('code', sa.String),
                                      sa.column('description', sa.String),
                                      sa.column('default', sa.Boolean),
                                      sa.column('type_code', sa.String),
                                      sa.column('hidden', sa.Boolean),
                                      sa.column('linked_product_code', sa.String),
                                      sa.column('need_review', sa.Boolean),
                                      sa.column('premium_only', sa.Boolean),
                                      sa.column('url', sa.String),
                                      )

    op.bulk_insert(
        product_code_table,
        [
            {'code': 'RPPR', 'description': 'Restricted Personal Property Registry', 'default': False,
             'type_code': 'INTERNAL', 'hidden': True, 'need_review': False, 'premium_only': True,
             'url': 'https://www.bcregistry.ca/ppr'}
        ]
    )

    # Query all orgs which are linked to BCOL.
    conn = op.get_bind()
    org_res = conn.execute(
        "select o.id, o.bcol_user_id from orgs o where bcol_user_id is not null and bcol_account_id is not null and "
        "status_code in ('ACTIVE', 'PENDING_STAFF_REVIEW'); "
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
            Product.create_subscription_from_bcol_profile(org_id[0], bcol_response.json().get('profileFlags'))
        except Exception as exc:
            print('Profile Error')
            print(exc)
            raise exc
    db.session.commit()

def downgrade():
    op.execute("DELETE FROM product_codes WHERE code in ('RPPR')")

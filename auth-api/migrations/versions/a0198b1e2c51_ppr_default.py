"""ppr default

Revision ID: a0198b1e2c51
Revises: e7f46c30d356
Create Date: 2021-06-08 13:18:24.141603

"""

# revision identifiers, used by Alembic.
from alembic import op
from flask import current_app
from sqlalchemy import text

from auth_api.models import db
from auth_api.services.products import Product
from auth_api.services.rest_service import RestService

# revision identifiers, used by Alembic.
revision = "a0198b1e2c51"
down_revision = "e7f46c30d356"
branch_labels = None
depends_on = None


def upgrade():
    # Query all orgs which are linked to BCOL.
    conn = op.get_bind()

    org_res = conn.execute(
        text(
            "select o.id, o.bcol_user_id from orgs o where bcol_user_id is not null and bcol_account_id is not null and status_code in ('ACTIVE', 'PENDING_STAFF_REVIEW');"
        )
    )
    orgs = org_res.fetchall()
    print("starting migration for BCOL products")
    if len(orgs) > 0:
        token = RestService.get_service_account_token()
    for org_id in orgs:
        try:
            print("Getting bcol profile for ", org_id[0], org_id[1])
            bcol_response = RestService.get(
                endpoint=current_app.config.get("BCOL_API_URL") + f"/profiles/{org_id[1]}", token=token
            )
            print("BCOL Response", bcol_response.json())
            Product.create_subscription_from_bcol_profile(org_id[0], bcol_response.json().get("profileFlags"))
        except Exception as exc:
            print("Profile Error")
            print(exc)
            raise exc
    db.session.commit()


def downgrade():
    pass

"""pending_approval view permission

Revision ID: c44fff21c830
Revises: e6e295695b9a
Create Date: 2021-06-25 09:30:56.448783

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

from auth_api.utils.custom_sql import CustomSql


# revision identifiers, used by Alembic.
revision = "c44fff21c830"
down_revision = "e6e295695b9a"
branch_labels = None
depends_on = None


def upgrade():
    permissions_table = table(
        "permissions",
        column("id", sa.Integer()),
        column("membership_type_code", sa.String(length=15)),
        column("org_status_code", sa.String(length=25)),
        column("actions", sa.String(length=100)),
    )
    op.execute("delete from permissions where actions='request_product_package'")
    conn = op.get_bind()
    res = conn.execute(text(f"select max(id) from permissions;"))
    latest_id = res.fetchall()[0][0]

    # Insert code values
    op.bulk_insert(
        permissions_table,
        [
            {
                "id": latest_id + 1,
                "membership_type_code": "ADMIN",
                "org_status_code": "PENDING_AFFIDAVIT_REVIEW",
                "actions": "view",
            }
        ],
    )


def downgrade():
    op.execute("delete from permissions where actions='view' and org_status_code= 'PENDING_AFFIDAVIT_REVIEW'")

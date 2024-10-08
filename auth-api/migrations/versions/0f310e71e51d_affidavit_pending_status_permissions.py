"""affidavit_pending_status_permissions

Revision ID: 0f310e71e51d
Revises: c10f494d7e10
Create Date: 2021-01-04 14:55:28.146682

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.sql import column, table

from auth_api.utils.custom_sql import CustomSql


# revision identifiers, used by Alembic.
revision = "0f310e71e51d"
down_revision = "c10f494d7e10"
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
    conn = op.get_bind()
    res = conn.execute(text(f"select max(id) from permissions;"))
    latest_id = res.fetchall()[0][0]
    op.bulk_insert(
        permissions_table,
        [
            {
                "id": latest_id + 1,
                "membership_type_code": "ADMIN",
                "org_status_code": "PENDING_AFFIDAVIT_REVIEW",
                "actions": "view_account",
            }
        ],
    )


def downgrade():
    op.execute(
        "delete from permissions where membership_type_code='ADMIN' and org_status_code='PENDING_AFFIDAVIT_REVIEW' and actions='view_account'"
    )

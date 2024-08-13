"""added view edit for NSF account

Revision ID: b72d4946fb3c
Revises: f7362101e761
Create Date: 2021-01-06 14:34:14.575613

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = "b72d4946fb3c"
down_revision = "f7362101e761"
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
                "org_status_code": "NSF_SUSPENDED",
                "actions": "edit",
            },
            {
                "id": latest_id + 2,
                "membership_type_code": "ADMIN",
                "org_status_code": "NSF_SUSPENDED",
                "actions": "view",
            },
        ],
    )


def downgrade():
    op.execute(
        "delete from permissions where membership_type_code='ADMIN' "
        "and org_status_code='NSF_SUSPENDED' and actions in ('view','edit')"
    )

"""permissions for FRCR review

Revision ID: eaef1147f25c
Revises: b72d4946fb3c
Create Date: 2021-01-09 08:11:26.337104

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = "eaef1147f25c"
down_revision = "b72d4946fb3c"
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
            {"id": (latest_id := latest_id + 1), "membership_type_code": "ADMIN", "actions": "change_payment_method"},
            {"id": (latest_id := latest_id + 1), "membership_type_code": "ADMIN", "actions": "change_pad_info"},
            {
                "id": (latest_id := latest_id + 1),
                "membership_type_code": "ADMIN",
                "org_status_code": "NSF_SUSPENDED",
                "actions": "change_pad_info",
            },
            {"id": (latest_id := latest_id + 1), "membership_type_code": "ADMIN", "actions": "view_auth_options"},
            {"id": latest_id + 1, "membership_type_code": "ADMIN", "actions": "change_statement_settings"},
        ],
    )
    op.execute("update permissions set actions='change_auth_options' where actions='set_auth_options'")


def downgrade():
    op.execute(
        "delete from permissions where membership_type_code='ADMIN' "
        "and actions in ('change_payment_method','change_pad_info','view_auth_options','change_statement_settings')"
    )
    op.execute("update permissions set actions=set_auth_options where actions='change_auth_options'")

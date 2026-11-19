"""35210 - add SBC_FIN_STAFF org type and permissions

Revision ID: c4e8f1a2b9d6
Revises: a3c1e9b7d2f4
Create Date: 2026-11-18 10:00:00.000000

"""

from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "c4e8f1a2b9d6"
down_revision = "a3c1e9b7d2f4"
branch_labels = None
depends_on = None

PERMISSIONS = [
    "change_org_name",
    "change_role",
    "manage_statements",
    "remove_business",
    "reset_otp",
    "reset_password",
    "transaction_history",
    "view_activitylog",
    "view_address",
    "view_admin_contact",
    "view_auth_options",
    "view_request_product_package",
    "view_user_loginsource",
    "view_active_accounts",
    "view_inactive_accounts",
    "view_business_registry_dashboard",
    "view_launch_titles",
    "view_rejected_tasks",
    "view_account_invitations",
    "view_pending_tasks",
    "view_suspended_accounts",
]


def upgrade():
    org_type_table = table("org_types", column("code", String), column("description", String), column("default", Boolean))
    op.bulk_insert(org_type_table, [{"code": "SBC_FIN_STAFF", "description": "SBC Finance Staff", "default": False}])

    permissions_table = table("permissions", column("membership_type_code", String), column("actions", String))
    op.bulk_insert(
        permissions_table, [{"membership_type_code": "SBC_FIN_STAFF", "actions": action} for action in PERMISSIONS]
    )


def downgrade():
    op.execute("delete from permissions where membership_type_code = 'SBC_FIN_STAFF'")
    op.execute("delete from org_types where code = 'SBC_FIN_STAFF'")
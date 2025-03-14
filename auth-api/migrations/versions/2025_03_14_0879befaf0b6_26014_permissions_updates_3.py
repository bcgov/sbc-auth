"""26014-permissions-updates-3

Revision ID: 0879befaf0b6
Revises: 2b69b3c83578
Create Date: 2025-03-14 09:04:07.238735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0879befaf0b6'
down_revision = '2b69b3c83578'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""INSERT INTO permissions (membership_type_code, actions) VALUES ('CC_STAFF', 'view_account_invitations');""")
    op.execute("""INSERT INTO permissions (membership_type_code, actions) VALUES ('CC_STAFF', 'view_pending_tasks');""")
    op.execute("""INSERT INTO permissions (membership_type_code, actions) VALUES ('CC_STAFF', 'view_suspended_accounts');""")

def downgrade():
    op.execute("delete from permissions where membership_type_code = 'CC_STAFF' and actions = 'view_account_invitations'")
    op.execute("delete from permissions where membership_type_code = 'CC_STAFF' and actions = 'view_pending_tasks'")
    op.execute("delete from permissions where membership_type_code = 'CC_STAFF' and actions = 'view_suspended_accounts'")

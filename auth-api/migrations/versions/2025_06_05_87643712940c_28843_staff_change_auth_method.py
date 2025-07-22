"""28843-staff-change-auth-method

Revision ID: 87643712940c
Revises: 6f2c09061fd3
Create Date: 2025-06-05 14:05:36.299601

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '87643712940c'
down_revision = '6f2c09061fd3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""INSERT INTO permissions (membership_type_code, actions) VALUES ('STAFF', 'change_auth_options');""")


def downgrade():
    op.execute("delete from permissions where membership_type_code = 'STAFF' and actions = 'change_auth_options'")

"""28809-Maximus-CC-permisssions-update

Revision ID: 00566833d2e0
Revises: 5a5a3a82f05c
Create Date: 2025-07-16 10:36:26.497627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00566833d2e0'
down_revision = '5a5a3a82f05c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""INSERT INTO permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'view_business_registry_dashboard');""")
    op.execute("""INSERT INTO permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'view_launch_titles');""")
    op.execute("""INSERT INTO permissions (membership_type_code, actions) VALUES ('CC_STAFF', 'view_business_registry_dashboard');""")
    op.execute("""INSERT INTO permissions (membership_type_code, actions) VALUES ('CC_STAFF', 'view_launch_titles');""")

    op.execute("delete from permissions where membership_type_code = 'MAXIMUS_STAFF' and actions = 'view_all_products_launcher'")
    op.execute("delete from permissions where membership_type_code = 'CC_STAFF' and actions = 'view_all_products_launcher'")



def downgrade():
    op.execute("delete from permissions where membership_type_code = 'MAXIMUS_STAFF' and actions = 'view_business_registry_dashboard'")
    op.execute("delete from permissions where membership_type_code = 'MAXIMUS_STAFF' and actions = 'view_launch_titles'")
    op.execute("delete from permissions where membership_type_code = 'CC_STAFF' and actions = 'view_business_registry_dashboard'")
    op.execute("delete from permissions where membership_type_code = 'CC_STAFF' and actions = 'view_launch_titles'")

    op.execute("""INSERT INTO permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'view_all_products_launcher');""")
    op.execute("""INSERT INTO permissions (membership_type_code, actions) VALUES ('CC_STAFF', 'view_all_products_launcher');""")

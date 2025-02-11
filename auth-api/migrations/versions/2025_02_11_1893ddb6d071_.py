"""Migration to add in new permission EDIT_USER for admin

Revision ID: 1893ddb6d071
Revises: 7425171449c9
Create Date: 2025-02-11 05:56:03.631513

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1893ddb6d071'
down_revision = '7425171449c9'
branch_labels = None
depends_on = None


def upgrade():
  op.execute("""INSERT INTO permissions (membership_type_code, actions)
    SELECT 'ADMIN', 'edit_user'
    WHERE NOT EXISTS (
        SELECT 1 FROM permissions 
        WHERE membership_type_code = 'ADMIN' 
        AND actions = 'edit_user'
    );""")

def downgrade():
  op.execute("delete from permissions where membership_type_code = 'ADMIN' and actions = 'edit_user'")

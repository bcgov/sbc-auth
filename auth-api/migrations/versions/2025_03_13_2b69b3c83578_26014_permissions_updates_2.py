"""26014-permissions-updates-2

Revision ID: 2b69b3c83578
Revises: 2ef3f0be3759
Create Date: 2025-03-13 13:40:59.972418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b69b3c83578'
down_revision = '2ef3f0be3759'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('COORDINATOR', 'edit_user');""")


def downgrade():
    op.execute("delete from permissions where membership_type_code = 'COORDINATOR' and actions = 'edit_user'")

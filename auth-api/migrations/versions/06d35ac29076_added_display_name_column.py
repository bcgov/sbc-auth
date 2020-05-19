"""added display name column

Revision ID: 06d35ac29076
Revises: 08063ceec05d
Create Date: 2020-05-18 08:15:08.901631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06d35ac29076'
down_revision = '08063ceec05d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('membership_type', sa.Column('display_name', sa.String(length=50), nullable=True))
    op.execute("UPDATE membership_type SET display_name = 'User' where code= 'MEMBER'")
    op.execute("UPDATE membership_type SET display_name = 'Account coordinator' where code = 'ADMIN'")
    op.execute("UPDATE membership_type SET display_name = 'Account administrator' where code = 'OWNER'")


def downgrade():
    op.drop_column('membership_type', 'display_name')

"""add view address permission to admin

Revision ID: 39b4f331c003
Revises: 41fa6588c76e
Create Date: 2024-05-30 20:21:15.422128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39b4f331c003'
down_revision = '41fa6588c76e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "INSERT INTO permissions (id, membership_type_code, actions) VALUES (84, 'ADMIN', 'view_address')"
    )


def downgrade():
    op.execute('DELETE FROM permissions WHERE id=84')

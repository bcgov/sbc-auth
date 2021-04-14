"""merge heads

Revision ID: d804bcead371
Revises: 68c71d35f671, 89b1e9096ad4
Create Date: 2021-04-06 11:04:55.040110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd804bcead371'
down_revision = ('68c71d35f671', '89b1e9096ad4')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

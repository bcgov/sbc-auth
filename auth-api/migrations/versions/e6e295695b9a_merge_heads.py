"""merge heads

Revision ID: e6e295695b9a
Revises: ca5c15ff55f0, b5578f6deba6
Create Date: 2021-06-18 14:14:47.537481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6e295695b9a'
down_revision = ('ca5c15ff55f0', 'b5578f6deba6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

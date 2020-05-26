"""merge commits

Revision ID: ef8a9847f953
Revises: bab2eefb9412, 71d7c605c31b
Create Date: 2020-05-25 17:11:27.242643

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef8a9847f953'
down_revision = ('bab2eefb9412', '71d7c605c31b')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

"""merge heads

Revision ID: d1b167ef61da
Revises: eff007a689cb, 032248a1b370
Create Date: 2020-09-10 15:14:57.527181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1b167ef61da'
down_revision = ('eff007a689cb', '032248a1b370')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

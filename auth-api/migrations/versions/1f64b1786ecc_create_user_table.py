"""create user table

Revision ID: 1f64b1786ecc
Revises: 
Create Date: 2019-04-10 11:48:46.966312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f64b1786ecc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('roles', sa.Unicode(1000), nullable=False),
    )


def downgrade():
    op.drop_table('user')

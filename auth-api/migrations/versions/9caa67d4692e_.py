"""empty message

Revision ID: 9caa67d4692e
Revises: 48bd1f6e6c99
Create Date: 2019-07-19 15:16:00.111284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9caa67d4692e'
down_revision = '48bd1f6e6c99'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'org_type', ['code'])
    op.create_unique_constraint(None, 'payment_type', ['code'])
    op.add_column('user', sa.Column('roles', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'roles')
    op.drop_constraint(None, 'payment_type', type_='unique')
    op.drop_constraint(None, 'org_type', type_='unique')
    # ### end Alembic commands ###

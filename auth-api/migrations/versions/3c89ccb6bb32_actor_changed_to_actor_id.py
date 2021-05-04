"""actor changed to actor_id

Revision ID: 3c89ccb6bb32
Revises: d0392ebda924
Create Date: 2021-05-03 05:29:19.193588

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c89ccb6bb32'
down_revision = 'd0392ebda924'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('activity_logs', 'actor')
    op.add_column('activity_logs', sa.Column('actor_id', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('activity_logs', 'actor_id')
    op.add_column('activity_logs', sa.Column('actor', sa.String(), nullable=True))

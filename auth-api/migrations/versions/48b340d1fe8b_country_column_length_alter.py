"""country column length alter

Revision ID: 48b340d1fe8b
Revises: 0ab62b841b88
Create Date: 2020-04-23 11:57:53.244868

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48b340d1fe8b'
down_revision = '0ab62b841b88'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('contact', 'country',
                    existing_type=sa.String(length=2),
                    type_=sa.String(length=20))


def downgrade():
    op.alter_column('contact', 'country',
                    existing_type=sa.String(length=20),
                    type_=sa.String(length=2))


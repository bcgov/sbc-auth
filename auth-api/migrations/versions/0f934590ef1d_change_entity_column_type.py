"""change entity column type

Revision ID: 0f934590ef1d
Revises: c9be42568338
Create Date: 2019-07-29 14:23:03.664656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f934590ef1d'
down_revision = 'c9be42568338'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('entity', 'business_identifier', existing_type=sa.Integer(), type_=sa.String(75))


def downgrade():
    op.alter_column('entity', 'business_identifier', existing_type=sa.String(75), type_=sa.Integer())

"""Add folio number to entity table

Revision ID: 09c44f82c03c
Revises: 68e2f43b9d22
Create Date: 2020-03-20 10:33:31.402269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09c44f82c03c'
down_revision = '68e2f43b9d22'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('entity', sa.Column('folio_number', sa.String(length=50), nullable=True))


def downgrade():
    op.drop_column('entity', 'folio_number')

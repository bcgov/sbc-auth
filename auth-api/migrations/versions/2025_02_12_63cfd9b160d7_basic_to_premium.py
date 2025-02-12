"""Migrate all basic accounts to premium.

Revision ID: 63cfd9b160d7
Revises: 1893ddb6d071
Create Date: 2025-02-12 10:30:52.935100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63cfd9b160d7'
down_revision = '1893ddb6d071'
branch_labels = None
depends_on = None


def upgrade():
      op.execute("update orgs set type_code = 'PREMIUM' where type_code = 'BASIC'")


def downgrade():
    pass

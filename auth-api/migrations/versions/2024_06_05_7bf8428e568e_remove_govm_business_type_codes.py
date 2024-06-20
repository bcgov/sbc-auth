"""remove GOVM from business_type_codes

Revision ID: 7bf8428e568e
Revises: 1e4b6359f470
Create Date: 2024-06-05 15:43:49.638951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bf8428e568e'
down_revision = '1e4b6359f470'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM business_type_codes WHERE code = 'GOVM'")


def downgrade():
    op.execute(
        """
        INSERT INTO business_type_codes (code, description, default)
        VALUES ('GOVM', 'BC GOVERNMENT MINISTRY', False)
        """
    )

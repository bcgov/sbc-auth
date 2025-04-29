"""Clear out the sandbox affiliations

Revision ID: bddf9fe7468c
Revises: 0879befaf0b6
Create Date: 2025-04-29 09:49:31.783306

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bddf9fe7468c'
down_revision = '0879befaf0b6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('delete from affiliations where environment=\'sandbox\'')

def downgrade():
    pass
    
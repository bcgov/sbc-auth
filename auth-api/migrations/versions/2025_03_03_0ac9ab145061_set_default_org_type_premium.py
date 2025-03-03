"""Org type default to premium

Revision ID: 0ac9ab145061
Revises: 7f48833011c3
Create Date: 2025-03-03 15:25:16.906525

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0ac9ab145061'
down_revision = '7f48833011c3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("update org_types set default = 't' where type_code = 'PREMIUM'")
    op.execute("update org_types set default = 'f' where type_code = 'BASIC'")

def downgrade():
    op.execute("update org_types set default = 'f' where type_code = 'PREMIUM'")
    op.execute("update org_types set default = 't' where type_code = 'BASIC'")
        

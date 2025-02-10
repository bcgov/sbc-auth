"""Remove products coodinator

Revision ID: 7425171449c9
Revises: 3f5b8a19ce42
Create Date: 2025-02-10 09:53:25.604521

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7425171449c9'
down_revision = '3f5b8a19ce42'
branch_labels = None
depends_on = None

def upgrade():
  op.execute("delete from permissions where membership_type_code = 'COORDINATOR' and actions = 'view_request_product_package'")

def downgrade():
  op.execute("insert into permissions (membership_type_code, actions) values ('COORDINATOR', 'view_request_product_package')")

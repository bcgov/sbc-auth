"""Rename CONTACT_CENTER_STAFF to CC_STAFF in org_types

Revision ID: 61eb9f696d5e
Revises: 7f48833011c3
Create Date: 2025-03-03 11:28:30.538876

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61eb9f696d5e'
down_revision = '7f48833011c3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        UPDATE org_types
        SET code = 'CC_STAFF'
        WHERE code = 'CONTACT_CENTRE_STAFF';
    """)


def downgrade():
    op.execute("""
        UPDATE org_types
        SET code = 'CONTACT_CENTRE_STAFF'
        WHERE code = 'CC_STAFF';
    """)

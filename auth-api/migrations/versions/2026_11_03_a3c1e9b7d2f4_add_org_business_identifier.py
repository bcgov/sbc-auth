"""add business_identifier to orgs

Revision ID: a3c1e9b7d2f4
Revises: 5beab65ee0a4
Create Date: 2026-11-03 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a3c1e9b7d2f4"
down_revision = "5beab65ee0a4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("orgs", sa.Column("business_identifier", sa.String(length=75), nullable=True))
    op.add_column("orgs_history", sa.Column("business_identifier", sa.String(length=75), nullable=True))
    op.create_index(
        "ix_orgs_business_identifier",
        "orgs",
        ["business_identifier"],
        unique=False,
        postgresql_where=sa.text("business_identifier IS NOT NULL"),
    )


def downgrade():
    op.drop_index("ix_orgs_business_identifier", table_name="orgs")
    op.drop_column("orgs_history", "business_identifier")
    op.drop_column("orgs", "business_identifier")

"""Add UNAFFILIATED_EMAIL affiliation invitation type and make from_org_id nullable.

Revision ID: a1b2c3d4e5f6
Revises: 57e4f388c6ed
Create Date: 2026-02-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '57e4f388c6ed'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "INSERT INTO affiliation_invitation_types (code, description, \"default\") "
        "VALUES ('UNAFFILIATED_EMAIL', "
        "'An affiliation invitation sent to entity email when no org affiliation exists yet', "
        "false)"
    )
    op.alter_column('affiliation_invitations', 'from_org_id', nullable=True)


def downgrade():
    op.alter_column('affiliation_invitations', 'from_org_id', nullable=False)
    op.execute("DELETE FROM affiliation_invitation_types WHERE code = 'UNAFFILIATED_EMAIL'")

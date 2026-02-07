"""Add UNAFFILIATED_EMAIL affiliation invitation type and make from_org_id nullable.

Revision ID: a1b2c3d4e5f6
Revises: 57e4f388c6ed
Create Date: 2026-02-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Boolean, String


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '57e4f388c6ed'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('affiliation_invitation_types', 'code', type_=sa.String(20), existing_type=sa.String(15))
    op.alter_column('affiliation_invitations', 'type', type_=sa.String(20), existing_type=sa.String(15))

    ait = sa.table('affiliation_invitation_types',
                   sa.column('code', String),
                   sa.column('description', String),
                   sa.column('default', Boolean)
                   )
    op.bulk_insert(ait,
                   [
                       {'code': 'UNAFFILIATED_EMAIL', 'description': 'Invitation sent to entity email when no org affiliation exists', 'default': False}
                   ])
    op.alter_column('affiliation_invitations', 'from_org_id', nullable=True)
    op.alter_column('affiliation_invitations', 'sender_id', nullable=True, existing_type=sa.Integer())


def downgrade():
    op.alter_column('affiliation_invitations', 'sender_id', nullable=False, existing_type=sa.Integer())
    op.alter_column('affiliation_invitations', 'from_org_id', nullable=False)
    op.execute("DELETE FROM affiliation_invitation_types WHERE code = 'UNAFFILIATED_EMAIL'")
    op.alter_column('affiliation_invitations', 'type', type_=sa.String(15), existing_type=sa.String(20))
    op.alter_column('affiliation_invitation_types', 'code', type_=sa.String(15), existing_type=sa.String(20))

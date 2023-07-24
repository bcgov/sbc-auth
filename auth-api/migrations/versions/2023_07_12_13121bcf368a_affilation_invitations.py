"""affilation_invitations

Revision ID: 13121bcf368a
Revises: d53a79e9cc89
Create Date: 2023-07-12 14:23:09.044117

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13121bcf368a'
down_revision = 'd53a79e9cc89'
branch_labels = None
depends_on = None


def upgrade():
    affiliation_invitation_type_table = op.create_table('affiliation_invitation_types',
                                            sa.Column('code', sa.String(length=15), nullable=False),
                                            sa.Column('description', sa.String(length=100), nullable=False),
                                            sa.Column('default', sa.Boolean(), nullable=False),
                                            sa.PrimaryKeyConstraint('code')
                                            )

    op.bulk_insert(
        affiliation_invitation_type_table,
        [
            {'code': 'EMAIL', 'description': 'An affiliation invitation initiated through email on file for an entity', 'default': True},
            {'code': 'PASSCODE', 'description': 'An affiliation invitation initiated through a valid passcode for an entity', 'default': False}
        ]
    )


    op.create_table('affiliation_invitations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_org_id', sa.Integer(), nullable=False),
    sa.Column('to_org_id', sa.Integer(), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=False),
    sa.Column('affiliation_id', sa.Integer(), nullable=True),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('approver_id', sa.Integer(), nullable=True),
    sa.Column('recipient_email', sa.String(length=100), nullable=False),
    sa.Column('sent_date', sa.DateTime(), nullable=False),
    sa.Column('accepted_date', sa.DateTime(), nullable=True),
    sa.Column('token', sa.String(length=150), nullable=True),
    sa.Column('invitation_status_code', sa.String(length=15), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('modified_by_id', sa.Integer(), nullable=True),
    sa.Column('login_source', sa.String(length=20), nullable=True),
    sa.Column('type', sa.String(length=15), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['invitation_status_code'], ['invitation_statuses.code'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['approver_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['from_org_id'], ['orgs.id'], ),
    sa.ForeignKeyConstraint(['to_org_id'], ['orgs.id'], ),
    sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ),
    sa.ForeignKeyConstraint(['type'], ['affiliation_invitation_types.code'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('affiliation_invitations')
    op.drop_table('affiliation_invitation_types')

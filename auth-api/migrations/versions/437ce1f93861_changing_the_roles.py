"""changing the roles

Revision ID: 437ce1f93861
Revises: 4efb2fdcc1ab
Create Date: 2020-05-19 12:35:28.744739

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '437ce1f93861'
down_revision = '4efb2fdcc1ab'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('membership_type', 'label', existing_type=sa.String(length=100), type_=sa.String(length=200))
    op.drop_constraint('membership_membership_type_code_fkey', 'membership', type_='foreignkey')
    op.drop_constraint('invitation_membership_membership_type_code_fkey', 'invitation_membership', type_='foreignkey')
    # add new column
    op.add_column('membership_type', sa.Column('display_name', sa.String(length=50), nullable=True))
    op.add_column('membership_type', sa.Column('display_order', sa.Integer(), nullable=True))
    # change roles in membership_type
    op.execute(
        "UPDATE membership_type SET code = 'USER' ,icon='mdi-account-outline', label='Submit searches and filings, add / remove businesses', display_name = 'User',display_order = 1 where code= 'MEMBER'")
    op.execute(
        "UPDATE membership_type SET code = 'COORDINATOR',icon='mdi-account-cog-outline' ,label='Submit searches and filings, add / remove businesses, add / remove team members',display_order = 2 , display_name = 'Account Coordinator' where code = 'ADMIN'")
    op.execute(
        "UPDATE membership_type SET code = 'ADMIN',icon='mdi-shield-account-outline',label='Submit searches and filings, add / remove businesses, add / remove team members, access financial statements, update payment methods',  "
        "display_name = 'Account Administrator',display_order = 3 where code = 'OWNER'")
    # change role name in membership
    op.execute("UPDATE membership SET membership_type_code = 'USER' where membership_type_code= 'MEMBER'")
    op.execute("UPDATE membership SET membership_type_code = 'COORDINATOR' where membership_type_code= 'ADMIN'")
    op.execute("UPDATE membership SET membership_type_code = 'ADMIN' where membership_type_code= 'OWNER'")

    op.execute("UPDATE invitation_membership SET membership_type_code = 'USER' where membership_type_code= 'MEMBER'")
    op.execute(
        "UPDATE invitation_membership SET membership_type_code = 'COORDINATOR' where membership_type_code= 'ADMIN'")
    op.execute("UPDATE invitation_membership SET membership_type_code = 'ADMIN' where membership_type_code= 'OWNER'")
    op.create_foreign_key('membership_membership_type_code_fkey', 'membership', 'membership_type',
                          ['membership_type_code'], ['code'])
    op.create_foreign_key('invitation_membership_membership_type_code_fkey', 'invitation_membership', 'membership_type',
                          ['membership_type_code'], ['code'])


def downgrade():
    op.drop_constraint('membership_membership_type_code_fkey', 'membership', type_='foreignkey')
    op.drop_constraint('invitation_membership_membership_type_code_fkey', 'invitation_membership', type_='foreignkey')
    op.drop_column('membership_type', 'display_name')
    op.drop_column('membership_type', 'display_order')
    op.execute(
        "UPDATE membership_type SET code = 'MEMBER',label='can add businesses, and file for a business.' where code= 'USER'")
    op.execute(
        "UPDATE membership_type SET code = 'OWNER',label='can add/remove team members and businesses, and file for a business.' where code = 'ADMIN'")
    op.execute(
        "UPDATE membership_type SET code = 'ADMIN',label='can add/remove team members, add businesses, and file for a business.'  where code = 'COORDINATOR'")
    op.execute("UPDATE membership SET membership_type_code = 'MEMBER' where membership_type_code= 'USER'")
    op.execute("UPDATE membership SET membership_type_code = 'OWNER' where membership_type_code= 'ADMIN'")
    op.execute("UPDATE membership SET membership_type_code = 'ADMIN' where membership_type_code= 'COORDINATOR'")

    op.execute("UPDATE invitation_membership SET membership_type_code = 'MEMBER' where membership_type_code= 'USER'")
    op.execute("UPDATE invitation_membership SET membership_type_code = 'OWNER' where membership_type_code= 'ADMIN'")
    op.execute(
        "UPDATE invitation_membership SET membership_type_code = 'ADMIN' where membership_type_code= 'COORDINATOR'")
    op.create_foreign_key('membership_membership_type_code_fkey', 'membership', 'membership_type',
                          ['membership_type_code'], ['code'])
    op.create_foreign_key('invitation_membership_membership_type_code_fkey', 'invitation_membership', 'membership_type',
                          ['membership_type_code'], ['code'])

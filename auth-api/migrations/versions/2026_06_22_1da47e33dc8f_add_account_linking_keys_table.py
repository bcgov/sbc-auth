"""add_account_linking_keys_table

Revision ID: 1da47e33dc8f
Revises: dfe9614f7fb0
Create Date: 2026-06-22 11:35:30.547054

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1da47e33dc8f'
down_revision = 'dfe9614f7fb0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('account_linking_keys',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('linking_key', sa.String(length=100), nullable=False,
              comment='Cryptographically random URL-safe secret shared with the vendor'),
    sa.Column('account_id', sa.Integer(), nullable=False,
              comment='Source account (e.g. lawfirm) whose affiliated businesses are accessible via this key'),
    sa.Column('vendor_account_id', sa.Integer(), nullable=True,
              comment='Vendor account (e.g. ALF) that is authorized to use this key; set at generation time'),
    sa.Column('status', sa.String(length=20), nullable=False, server_default='ACTIVE',
              comment='ACTIVE or REVOKED'),
    sa.Column('expires_on', sa.DateTime(timezone=True), nullable=False,
              comment='UTC timestamp after which the key is no longer valid'),
    sa.Column('last_used', sa.DateTime(timezone=True), nullable=True,
              comment='UTC timestamp of the most recent successful validation'),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('modified_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['orgs.id'], ),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['vendor_account_id'], ['orgs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('account_linking_keys', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_account_linking_keys_account_id'), ['account_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_account_linking_keys_linking_key'), ['linking_key'], unique=True)
        batch_op.create_index(batch_op.f('ix_account_linking_keys_vendor_account_id'), ['vendor_account_id'], unique=False)


def downgrade():
    with op.batch_alter_table('account_linking_keys', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_account_linking_keys_vendor_account_id'))
        batch_op.drop_index(batch_op.f('ix_account_linking_keys_linking_key'))
        batch_op.drop_index(batch_op.f('ix_account_linking_keys_account_id'))
    op.drop_table('account_linking_keys')

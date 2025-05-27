"""Add in entity mapping table.

Revision ID: 6f2c09061fd3
Revises: bddf9fe7468c
Create Date: 2025-05-22 17:21:47.908470

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6f2c09061fd3'
down_revision = 'bddf9fe7468c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('entities', sa.Column('is_loaded_lear', sa.Boolean(), nullable=False, server_default=sa.true()))

    op.create_table('entity_mapping',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('business_identifier', sa.String(length=75), nullable=True),
    sa.Column('bootstrap_identifier', sa.String(length=75), nullable=True),
    sa.Column('nr_identifier', sa.String(length=75), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('modified_by_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('entity_mapping', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_entity_mapping_bootstrap_identifier'), ['bootstrap_identifier'], unique=True)
        batch_op.create_index(batch_op.f('ix_entity_mapping_business_identifier'), ['business_identifier'], unique=True)
        batch_op.create_index(batch_op.f('ix_entity_mapping_nr_identifier'), ['nr_identifier'], unique=True)


def downgrade():
    with op.batch_alter_table('entity_mapping', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_entity_mapping_nr_identifier'))
        batch_op.drop_index(batch_op.f('ix_entity_mapping_business_identifier'))
        batch_op.drop_index(batch_op.f('ix_entity_mapping_bootstrap_identifier'))

    op.drop_table('entity_mapping')
    op.drop_column('entities', 'is_loaded_lear')

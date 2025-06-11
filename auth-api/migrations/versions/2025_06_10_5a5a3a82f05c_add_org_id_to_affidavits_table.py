"""add_org_id_to_affidavits_table

Revision ID: 5a5a3a82f05c
Revises: 87643712940c
Create Date: 2025-06-10 14:44:26.889499

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5a5a3a82f05c'
down_revision = '87643712940c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('affidavits', sa.Column('org_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint to orgs table
    op.create_foreign_key(
        'fk_affidavits_org_id', 
        'affidavits', 
        'orgs', 
        ['org_id'], 
        ['id']
    )
    
    op.create_index('ix_affidavits_org_id', 'affidavits', ['org_id'])
    
    op.add_column('affidavits_history', sa.Column('org_id', sa.Integer(), nullable=True))


def downgrade():
    # Remove from history table
    op.drop_column('affidavits_history', 'org_id')
    
    # Remove index
    op.drop_index('ix_affidavits_org_id', table_name='affidavits')
    
    # Remove foreign key constraint
    op.drop_constraint('fk_affidavits_org_id', 'affidavits', type_='foreignkey')
    
    # Remove column
    op.drop_column('affidavits', 'org_id')

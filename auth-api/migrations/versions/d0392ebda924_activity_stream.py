"""activity_stream 

Revision ID: d0392ebda924
Revises: 031a07fb0811
Create Date: 2021-04-19 19:15:16.830394

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0392ebda924'
down_revision = '031a07fb0811'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('activity_logs',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('actor', sa.String(length=250), nullable=True),
    sa.Column('action', sa.String(length=250), nullable=True),
    sa.Column('item_type', sa.String(length=250), nullable=True),
    sa.Column('item_name', sa.String(length=250), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('remote_addr', sa.String(length=250), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('modified_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_logs_action'), 'activity_logs', ['action'], unique=False)
    op.create_index(op.f('ix_activity_logs_item_name'), 'activity_logs', ['item_name'], unique=False)
    op.create_index(op.f('ix_activity_logs_item_type'), 'activity_logs', ['item_type'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_activity_logs_item_type'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_item_name'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_action'), table_name='activity_logs')
    op.drop_table('activity_logs')
    # ### end Alembic commands ###

"""Add in new table for account mailer for pubsub message processing.

Revision ID: b3a741249edc
Revises: e2d1d6417607
Create Date: 2024-05-15 14:52:45.780399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3a741249edc'
down_revision = 'e2d1d6417607'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pubsub_message_processing',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cloud_event_id', sa.String(length=250), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('message_type', sa.String(length=250), nullable=False),
    sa.Column('processed', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pubsub_message_processing_id'), 'pubsub_message_processing', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_pubsub_message_processing_id'), table_name='pubsub_message_processing')
    op.drop_table('pubsub_message_processing')

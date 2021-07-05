"""0003_support_multiple_attachment

Revision ID: 3c6a5fef5da3
Revises: 59345515423b
Create Date: 2020-05-13 14:55:22.162266

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c6a5fef5da3'
down_revision = '59345515423b'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('notification_contents', 'content')
    op.execute('ALTER SEQUENCE notification_contents_id_seq RENAME TO content_id_seq')

    op.create_table('attachment',
                sa.Column('id', sa.Integer(), nullable=False),
                sa.Column('file_name', sa.String(length=200), nullable=False),
                sa.Column('file_bytes', sa.LargeBinary(), nullable=False),
                sa.Column('attach_order', sa.Integer(), nullable=True),
                sa.Column('content_id', sa.Integer(), nullable=False),
                sa.ForeignKeyConstraint(['content_id'], ['content.id'], ),
                sa.PrimaryKeyConstraint('id')
                )


    op.execute('INSERT INTO attachment (file_name, file_bytes, content_id) '
               'SELECT attachment_name, attachment, id '
               'FROM content '
               'WHERE attachment_name is not NULL')

    op.drop_column('content', 'attachment_name')
    op.drop_column('content', 'attachment')

    op.add_column('notification', sa.Column('request_by', sa.String(length=100), nullable=True))

def downgrade():
    op.drop_column('notification', 'request_by')

    op.add_column('content', sa.Column('attachment_name', sa.String(length=200), nullable=True))
    op.add_column('content', sa.Column('attachment',sa.LargeBinary(), nullable=True))

    op.execute('UPDATE content nc '
               'SET (attachment_name, attachment) = '
               '(SELECT attachment_name, attachment '
               ' FROM attachment WHERE content_id = nc.id limit 1)')

    op.drop_table('attachment')
    op.rename_table('content', 'notification_contents')
    op.execute('ALTER SEQUENCE content_id_seq RENAME TO notification_contents_id_seq')

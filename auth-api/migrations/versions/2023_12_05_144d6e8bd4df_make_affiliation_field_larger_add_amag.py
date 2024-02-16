"""Add in amalgamation corp type and extend receipient fields to 8k

Revision ID: 144d6e8bd4df
Revises: 9e8d6b3de6d5
Create Date: 2023-12-05 11:42:32.349688

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '144d6e8bd4df'
down_revision = '9e8d6b3de6d5'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(f"insert into corp_types (code, description, \"default\") values ('ATMP', 'Amalgamation', 'f') on conflict (code) do nothing;")
    op.execute('alter table affiliation_invitations alter column recipient_email type varchar(8000);')

def downgrade():
    op.execute('delete from corp_types where code=\'ATMP\';')
    op.execute('alter table affiliation_invitations alter column recipient_email type varchar(100);')

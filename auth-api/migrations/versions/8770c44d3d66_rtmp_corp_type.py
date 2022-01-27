"""rtmp_corp_type

Revision ID: 8770c44d3d66
Revises: 342ec8814181
Create Date: 2022-01-26 12:08:32.789057

"""
from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '8770c44d3d66'
down_revision = '342ec8814181'
branch_labels = None
depends_on = None


def upgrade():
    corp_type_table = table('corp_types',
                            column('code', String),
                            column('desc', String),
                            column('default', Boolean)
                            )
    op.bulk_insert(
        corp_type_table,
        [
            {'code': 'RTMP', 'description': 'Registration', 'default': False}
        ]
    )


def downgrade():
    op.execute('delete from corp_types where code=\'RTMP\'')

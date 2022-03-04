"""SP&GP corp types

Revision ID: cd89e8e61dec
Revises: 8770c44d3d66
Create Date: 2022-03-03 21:25:30.741161

"""
from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = 'cd89e8e61dec'
down_revision = '8770c44d3d66'
branch_labels = None
depends_on = None


def upgrade():
    corp_type_table = table('corp_types',
                            column('code', String),
                            column('description', String),
                            column('default', Boolean)
                            )
    # Insert code values
    op.bulk_insert(
        corp_type_table,
        [
            {'code': 'SP', 'description': 'Sole Proprietorship', 'default': False},
            {'code': 'GP', 'description': 'General Partnership', 'default': False}
        ]
    )


def downgrade():
    op.execute("delete from corp_types where code in ('SP','GP')")

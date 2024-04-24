"""CTMP message

Revision ID: 51524729b99c
Revises: 824f5ef280c6
Create Date: 2024-04-23 14:50:24.894593

"""
from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '51524729b99c'
down_revision = '824f5ef280c6'
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
            {'code': 'CTMP', 'description': 'Continuation In', 'default': False},
            {'code': 'C', 'description': 'BC Limited Company Continuation In', 'default': False},
            {'code': 'CBEN', 'description': 'BC Benefit Company Continuation In', 'default': False},
            {'code': 'CUL', 'description': 'BC Unlimited Liability Company Continuation In', 'default': False}
        ]
    )
    op.execute("update from corp_types set description='BC Community Contribution Company Continuation In' where code='CCC'")


def downgrade():
    op.execute("delete from corp_types where code in ('CTMP','C', 'CBEN', 'CUL')")

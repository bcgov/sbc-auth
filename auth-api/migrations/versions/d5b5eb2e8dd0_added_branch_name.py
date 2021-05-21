"""added branch name

Revision ID: d5b5eb2e8dd0
Revises: 69a7e464fef3
Create Date: 2021-03-03 21:30:29.597634

"""
import sqlalchemy as sa
from alembic import op
# revision identifiers, used by Alembic.
from sqlalchemy.sql import column, table


revision = 'd5b5eb2e8dd0'
down_revision = '69a7e464fef3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('orgs', sa.Column('branch_name', sa.String(length=100), nullable=True))
    op.add_column('orgs_version', sa.Column('branch_name', sa.String(length=100), nullable=True))

    invitation_type_table = table('invitation_types',
                                            column('code', sa.String(length=15)),
                                            column('description', sa.String(length=100)),
                                            column('default', sa.Boolean())
                                            )

    op.bulk_insert(
        invitation_type_table,
        [
            {'code': 'GOVM', 'description': 'An invitation to activate a GOV Ministry account',
             'default': False},
        ]
    )


def downgrade():
    op.drop_column('orgs', 'branch_name')
    op.drop_column('orgs_version', 'branch_name')
    op.execute("DELETE from invitation_types WHERE code='GOVM'")

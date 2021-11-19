"""verified_user

Revision ID: 09dd4ea64775
Revises: d00101759be4
Create Date: 2021-11-19 13:05:57.935908

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '09dd4ea64775'
down_revision = 'd00101759be4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('verified', sa.Boolean(), nullable=True))
    op.add_column('users_version', sa.Column('verified', sa.Boolean(), autoincrement=False, nullable=True))
    membership_status_table = table('membership_status_codes',
                                    column('id', sa.Integer()),
                                    column('name', sa.String()),
                                    column('description', sa.String()))

    op.bulk_insert(
        membership_status_table,
        [
            {
                "id": 5,
                "name": "PENDING_STAFF_REVIEW",
                "description": "Pending Staff Review"
            }
        ]
    )


def downgrade():
    op.execute("delete from membership_status_codes where name='PENDING_STAFF_REVIEW';")
    op.drop_column('users_version', 'verified')
    op.drop_column('users', 'verified')

"""task_action

Revision ID: 9f3450623765
Revises: 09dd4ea64775
Create Date: 2021-12-02 12:51:18.312740

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '9f3450623765'
down_revision = '09dd4ea64775'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('action', sa.String(length=50), nullable=True))
    op.execute("update tasks set action='ACCOUNT_REVIEW' where upper(type)='GOVM';")
    op.execute("update tasks set action='PRODUCT_REVIEW' where relationship_type='PRODUCT';")
    op.execute("update tasks set action='AFFIDAVIT_REVIEW' where upper(type)='BCEID ADMIN';")
    op.execute("update tasks set action='AFFIDAVIT_REVIEW' where upper(type)='NEW ACCOUNT';")  # BCeID accounts
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'action')
    # ### end Alembic commands ###

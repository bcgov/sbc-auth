"""19421 - Qualified supplier - allow product subscription request resubmission

Revision ID: e65cc8ab51cc
Revises: 144d6e8bd4df
Create Date: 2024-02-12 11:34:44.872779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e65cc8ab51cc'
down_revision = '144d6e8bd4df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column('product_codes', sa.Column('can_resubmit', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('tasks', sa.Column('is_resubmitted', sa.Boolean(), nullable=False, server_default=sa.false()))

    op.execute("UPDATE public.product_codes "
               "SET can_resubmit=true "
               "WHERE code in('MHR_QSLN','MHR_QSHM','MHR_QSHD')")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.drop_column('product_codes', 'can_resubmit')
    op.drop_column('tasks', 'is_resubmitted')
    # ### end Alembic commands ###

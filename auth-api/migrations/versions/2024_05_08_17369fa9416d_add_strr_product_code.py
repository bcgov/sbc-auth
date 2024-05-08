"""empty message

Revision ID: 17369fa9416d
Revises: 51524729b99c
Create Date: 2024-05-08 11:23:49.995943

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '17369fa9416d'
down_revision = '51524729b99c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("INSERT INTO public.product_codes "
               "(code, description,\"default\", type_code, hidden, need_review, need_system_admin, premium_only, url) "
               "VALUES "
               "('STRR', 'Short Term Rental Registry', false, 'INTERNAL', true, false, false, false,'')")
    op.execute("commit")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DELETE FROM product_codes WHERE code in ('STRR')")
    op.execute("commit")
    # ### end Alembic commands ###

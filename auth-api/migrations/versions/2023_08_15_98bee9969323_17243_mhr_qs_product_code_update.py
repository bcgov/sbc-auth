"""17243_mhr_qs_product_code_update

Revision ID: 98bee9969323
Revises: 628b52a95bad
Create Date: 2023-08-15 08:38:16.786130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98bee9969323'
down_revision = '628b52a95bad'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE public.product_codes "
               "SET description='Manufactured Home Registry – Lawyers and Notaries'"
               "WHERE code='MHR_QSLN'")
    op.execute("UPDATE public.product_codes "
               "SET description='Manufactured Home Registry – Manufacturers'"
               "WHERE code='MHR_QSHM'")
    op.execute("UPDATE public.product_codes "
               "SET description='Manufactured Home Registry – Home Dealers'"
               "WHERE code='MHR_QSHD'")


def downgrade():
    op.execute("UPDATE public.product_codes "
               "SET description='Qualified Supplier - Lawyers and Notaries'"
               "WHERE code='MHR_QSLN'")
    op.execute("UPDATE public.product_codes "
               "SET description='Qualified Supplier - Home Manufacturers'"
               "WHERE code='MHR_QSHM'")
    op.execute("UPDATE public.product_codes "
               "SET description='Qualified Supplier - Home Dealers'"
               "WHERE code='MHR_QSHD'")



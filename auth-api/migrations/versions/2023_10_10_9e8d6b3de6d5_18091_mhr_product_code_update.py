"""18091-mhr-product-code-update

Revision ID: 9e8d6b3de6d5
Revises: 0f7e04a673f7
Create Date: 2023-10-10 07:36:07.599629

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e8d6b3de6d5'
down_revision = '0f7e04a673f7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE public.product_codes "
               "SET keycloak_group='mhr_dealership' "
               "WHERE code='MHR_QSHD'")


def downgrade():
    op.execute("UPDATE public.product_codes "
               "SET keycloak_group='mhr_general_user' "
               "WHERE code='MHR_QSHD'")

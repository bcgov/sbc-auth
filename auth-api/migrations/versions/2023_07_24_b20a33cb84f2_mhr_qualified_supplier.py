"""mhr_qualified_supplier

Revision ID: b20a33cb84f2
Revises: 13121bcf368a
Create Date: 2023-07-24 13:12:24.781629

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b20a33cb84f2'
down_revision = '13121bcf368a'
branch_labels = None
depends_on = None


def upgrade():

    # add parent_code column to allow for sub product hierarchy
    op.add_column('product_codes', sa.Column('parent_code', sa.String(length=15), nullable=True))

    # add external_source_id to tasks to capture an identifier for an external resource to retrieve
    # task related details managed by an external system - MHR Qualified Supplier for this particular change
    op.add_column('tasks',
                  sa.Column('external_source_id', sa.String(length=75), nullable=True))

    # Add MHR sub product codes
    op.execute("INSERT INTO product_codes "
               "(code, description,\"default\", type_code, hidden, need_review, premium_only, url, keycloak_group, "
               "parent_code) "
               "VALUES "
               "('MHR_QSLN', 'Qualified Supplier - Lawyers and Notaries', false, 'INTERNAL', false, true, true, "
               "'https://www.bcregistry.ca/ppr', 'mhr_qualified_user', 'MHR')")
    op.execute("INSERT INTO product_codes "
               "(code, description,\"default\", type_code, hidden, need_review, premium_only, url, keycloak_group, "
               "parent_code) "
               "VALUES "
               "('MHR_QSHM', 'Qualified Supplier - Home Manufacturers', false, 'INTERNAL', false, true, true, "
               "'https://www.bcregistry.ca/ppr', 'mhr_manufacturer', 'MHR')")
    op.execute("INSERT INTO product_codes "
               "(code, description,\"default\", type_code, hidden, need_review, premium_only, url, keycloak_group, "
               "parent_code) "
               "VALUES "
               "('MHR_QSHD', 'Qualified Supplier - Home Dealers', false, 'INTERNAL', false, true, true, "
               "'https://www.bcregistry.ca/ppr', 'mhr_general_user', 'MHR')")


def downgrade():
    op.execute("DELETE FROM product_codes WHERE code in ('MHR_QSLN')")
    op.execute("DELETE FROM product_codes WHERE code in ('MHR_QSHM')")
    op.execute("DELETE FROM product_codes WHERE code in ('MHR_QSHD')")
    op.drop_column('product_codes', 'parent_code')
    op.drop_column('tasks', 'external_source_id')

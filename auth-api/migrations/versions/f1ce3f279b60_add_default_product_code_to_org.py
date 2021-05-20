"""empty message

Revision ID: f1ce3f279b60
Revises: 933ecac34eb4
Create Date: 2020-07-02 10:56:49.895541

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f1ce3f279b60'
down_revision = '933ecac34eb4'
branch_labels = None
depends_on = None


def upgrade():
    ## Insert default product code value for all orgs
    op.execute("insert into product_subscription (org_id, product_code, created_by_id) \
                select id, 'BUSINESS', created_by_id \
                    FROM org where id not in (select org_id from product_subscription);")

def downgrade():
    op.execute("delete from product_subscription where created is NULL;")

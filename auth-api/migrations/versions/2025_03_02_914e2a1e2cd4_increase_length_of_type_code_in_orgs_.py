"""Increase length of type_code column in orgs table

Revision ID: 914e2a1e2cd4
Revises: 7f48833011c3
Create Date: 2025-03-02 22:16:51.568851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '914e2a1e2cd4'
down_revision = '7f48833011c3'
branch_labels = None
depends_on = None

from auth_api.utils.custom_sql import CustomSql

authorizations_view = CustomSql(
    "authorizations_view",
    " SELECT e.business_identifier,"
    "e.name AS entity_name,"
    "e.folio_number,"
    "e.corp_type_code,"
    "m.membership_type_code AS org_membership,"
    "u.keycloak_guid,"
    "u.id AS user_id,"
    "o.id AS org_id,"
    "o.name AS org_name,"
    "o.status_code,"
    "o.type_code AS org_type,"
    "ps.product_code,"
    "o.bcol_user_id,"
    "o.bcol_account_id"
    " FROM memberships m "
    "LEFT JOIN orgs o ON m.org_id = o.id "
    "LEFT JOIN users u ON u.id = m.user_id "
    "LEFT JOIN affiliations a ON o.id = a.org_id "
    "LEFT JOIN entities e ON e.id = a.entity_id "
    "LEFT JOIN product_subscriptions ps ON ps.org_id = o.id "
    "WHERE m.status = 1;",
)


def upgrade():
    op.execute(f"DROP VIEW IF EXISTS {authorizations_view.name}")
    op.alter_column('orgs', 'type_code', type_=sa.String(length=30))
    op.execute(f"CREATE VIEW {authorizations_view.name} AS {authorizations_view.sql}")

def downgrade():
    op.execute(f"DROP VIEW IF EXISTS {authorizations_view.name}")
    op.alter_column('orgs', 'type_code', type_=sa.String(length=15))
    op.execute(f"CREATE VIEW {authorizations_view.name} AS {authorizations_view.sql}")

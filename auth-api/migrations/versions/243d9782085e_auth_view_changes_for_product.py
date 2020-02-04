"""auth_view_changes_for_product

Revision ID: 243d9782085e
Revises: cadc28cb38d3
Create Date: 2020-02-04 12:51:13.102152

"""
from alembic import op
import sqlalchemy as sa
from auth_api.utils.custom_sql import CustomSql


# revision identifiers, used by Alembic.
revision = '243d9782085e'
down_revision = 'cadc28cb38d3'
branch_labels = None
depends_on = None

authorizations_view = CustomSql('authorizations_view',
                                'SELECT e.business_identifier, '
                                'e.NAME AS entity_name, '
                                'e.corp_type_code, '
                                'm.membership_type_code AS org_membership, '
                                'u.keycloak_guid, '
                                'u.id AS user_id, '
                                'o.id AS org_id, '
                                'o.type_code AS org_type, '
                                'ps.product_code AS product_code, '
                                '(SELECT String_agg(prc.code, \',\') '
                                '   FROM   product_role pr, '
                                '   product_role_code prc '
                                'WHERE  pr.product_subscription_id = ps.id '
                                '   AND prc.id = pr.product_role_id) AS roles '
                                'FROM   membership m '
                                '   LEFT JOIN org o '
                                '       ON m.org_id = o.id '
                                '   LEFT JOIN "user" u '
                                '       ON u.id = m.user_id '
                                '   LEFT JOIN affiliation a '
                                '       ON o.id = a.org_id '
                                ' LEFT JOIN entity e '
                                '   ON e.id = a.entity_id '
                                ' LEFT JOIN product_subscription ps '
                                '   ON ps.org_id = o.id '
                                ' WHERE  m.status = 1;')

def upgrade():
    op.execute(f'DROP VIEW IF EXISTS {authorizations_view.name}')
    op.execute(f'CREATE VIEW {authorizations_view.name} AS {authorizations_view.sql}')


def downgrade():
    op.execute(f'DROP VIEW {authorizations_view.name}')

"""auth_view_adding_payment_info

Revision ID: c7d122dc4e06
Revises: 06eda339e0d5
Create Date: 2020-03-25 16:49:43.989363

"""
from alembic import op
import sqlalchemy as sa
from auth_api.utils.custom_sql import CustomSql


# revision identifiers, used by Alembic.
revision = 'c7d122dc4e06'
down_revision = '06eda339e0d5'
branch_labels = None
depends_on = None

authorizations_view = CustomSql('authorizations_view',
                                'SELECT '
                                '   e.business_identifier, '
                                '   e.name AS entity_name, '
                                '   e.folio_number AS folio_number, '
                                '   e.corp_type_code, '
                                '   m.membership_type_code AS org_membership, '
                                '   u.keycloak_guid, '
                                '   u.id AS user_id, '
                                '   o.id AS org_id, '
                                '   o.name AS org_name, '
                                '   o.type_code AS org_type, '
                                '   ps.product_code AS product_code, '
                                '   pay.preferred_payment_code as preferred_payment_code, '
                                '   pay.bcol_user_id as bcol_user_id, '
                                '   pay.bcol_account_id as bcol_account_id, '
                                '   (SELECT String_agg(prc.code, \',\') '
                                '       FROM   product_subscription_role pr, '
                                '       product_role_code prc '
                                '       WHERE  pr.product_subscription_id = ps.id '
                                '       AND prc.id = pr.product_role_id) AS ROLES '
                                'FROM   '
                                '   membership m '
                                '   left join org o '
                                '   ON m.org_id = o.id '
                                '   left join "user" u '
                                '   ON u.id = m.user_id '
                                '   left join affiliation a '
                                '   ON o.id = a.org_id '
                                '   left join entity e '
                                '   ON e.id = a.entity_id '
                                '   left join product_subscription ps '
                                '   ON ps.org_id = o.id '
                                '   left join account_payment_settings pay '
                                '   ON pay.org_id = o.id '
                                'WHERE '
                                '   m.status = 1; ')

def upgrade():
    op.execute(f'DROP VIEW IF EXISTS {authorizations_view.name}')
    op.execute(f'CREATE VIEW {authorizations_view.name} AS {authorizations_view.sql}')


def downgrade():
    op.execute(f'DROP VIEW {authorizations_view.name}')
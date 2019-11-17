"""update auth view add status check
status column introduced in membership. The view should only fetch data for active users.

Revision ID: dede70a6df1e
Revises: e27800c90c8a
Create Date: 2019-11-17 08:30:51.449943

"""
from alembic import op
import sqlalchemy as sa
from auth_api.utils.custom_sql import CustomSql

# revision identifiers, used by Alembic.
revision = 'dede70a6df1e'
down_revision = 'e27800c90c8a'
branch_labels = None
depends_on = None

authorizations_view = CustomSql('authorizations_view',
                                ' SELECT e.business_identifier, e.name AS entity_name, m.membership_type_code AS org_membership, u.keycloak_guid, u.id AS user_id, o.id AS org_id, o.type_code AS org_type'
                                ' FROM (( ( membership m left join org o on m.org_id = o.id ) '
                                'left join "user" u on u.id = m.user_id ) '
                                'left join affiliation a on o.id = a.org_id) '
                                'left join entity e on e.id = a.entity_id '
                                'where m.status =1 ')


def upgrade():
    op.execute(f'DROP VIEW IF EXISTS {authorizations_view.name}')
    op.execute(f'CREATE VIEW {authorizations_view.name} AS {authorizations_view.sql}')


def downgrade():
    op.execute(f'DROP VIEW {authorizations_view.name}')


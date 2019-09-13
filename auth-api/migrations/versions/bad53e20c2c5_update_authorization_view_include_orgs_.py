"""update_authorization_view_include_orgs_with_no_entity

Revision ID: bad53e20c2c5
Revises: 615db0d23fee
Create Date: 2019-09-13 13:31:53.621463

"""

# revision identifiers, used by Alembic.


from alembic import op

from auth_api.utils.custom_sql import CustomSql

revision = 'bad53e20c2c5'
down_revision = '615db0d23fee'
branch_labels = None
depends_on = None

authorizations_view = CustomSql('authorizations_view',
                                ' SELECT e.business_identifier, e.name AS entity_name, m.membership_type_code AS org_membership, u.keycloak_guid, u.id AS user_id, o.id AS org_id, o.type_code AS org_type FROM (( ( membership m left join org o on m.org_id = o.id ) left join "user" u on u.id = m.user_id ) left join affiliation a on o.id = a.org_id) left join entity e on e.id = a.entity_id ')


def upgrade():
    op.execute(f'DROP VIEW IF EXISTS {authorizations_view.name}')
    op.execute(f'CREATE VIEW {authorizations_view.name} AS {authorizations_view.sql}')


def downgrade():
    op.execute(f'DROP VIEW {authorizations_view.name}')

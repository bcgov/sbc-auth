"""Update authorizations view

Revision ID: 6848a30e95cd
Revises: 9f63681d5e6a
Create Date: 2019-09-20 10:59:21.600217

"""
from alembic import op

from auth_api.utils.custom_sql import CustomSql


# revision identifiers, used by Alembic.
revision = '6848a30e95cd'
down_revision = '9f63681d5e6a'
branch_labels = None
depends_on = None

authorizations_view = CustomSql('authorizations_view',
                                ' SELECT e.business_identifier, e.name AS entity_name, m.membership_type_code AS org_membership, u.keycloak_guid, u.id AS user_id, o.id AS org_id, o.type_code AS org_type FROM (( ( membership m left join org o on m.org_id = o.id ) left join "user" u on u.id = m.user_id ) left join affiliation a on o.id = a.org_id) left join entity e on e.id = a.entity_id ')

def upgrade():
    op.execute(f'DROP VIEW IF EXISTS {authorizations_view.name}')
    op.execute(f'CREATE VIEW {authorizations_view.name} AS {authorizations_view.sql}')


def downgrade():
    op.execute(f'DROP VIEW {authorizations_view.name}')

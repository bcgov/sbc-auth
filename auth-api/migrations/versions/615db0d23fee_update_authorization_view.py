"""update_authorization_view

Revision ID: 615db0d23fee
Revises: b32d868d628c
Create Date: 2019-09-13 11:48:26.512028

"""
from alembic import op

from auth_api.utils.custom_sql import CustomSql

# revision identifiers, used by Alembic.
revision = '615db0d23fee'
down_revision = 'b32d868d628c'
branch_labels = None
depends_on = None


authorizations_view = CustomSql('authorizations_view',
                                'select '
                                'e.business_identifier, e.name as entity_name, m.membership_type_code as org_membership, '
                                'u.keycloak_guid, u.id as user_id, o.id as org_id, o.type_code as org_type '
                                'from  '
                                'entity e,  affiliation a,  org o,  membership m,  user u '
                                'where  '
                                'e.id = a.entity_id  '
                                'and o.id = a.org_id  '
                                'and m.org_id = o.id  '
                                'and u.id = m.user_id ')


def upgrade():
    op.execute(f'DROP VIEW {authorizations_view.name}')
    op.execute(f'CREATE VIEW {authorizations_view.name} AS {authorizations_view.sql}')


def downgrade():
    op.execute(f'DROP VIEW {authorizations_view.name}')

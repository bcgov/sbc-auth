"""org status added to authorisation view 

Revision ID: 1c958b749a20
Revises: 75336ba7d252
Create Date: 2020-11-25 06:18:31.481932

"""
from alembic import op
import sqlalchemy as sa

from auth_api.utils.custom_sql import CustomSql
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '1c958b749a20'
down_revision = '75336ba7d252'
branch_labels = None
depends_on = None

authorizations_view_old = CustomSql('authorizations_view',
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
                                    '   o.bcol_user_id as bcol_user_id, '
                                    '   o.bcol_account_id as bcol_account_id, '
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
                                    'WHERE '
                                    '   m.status = 1')

authorizations_view_new = CustomSql('authorizations_view',
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
                                    '   o.status_code AS status_code, '
                                    '   o.type_code AS org_type, '
                                    '   ps.product_code AS product_code, '
                                    '   o.bcol_user_id as bcol_user_id, '
                                    '   o.bcol_account_id as bcol_account_id, '
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
                                    'WHERE '
                                    '   m.status = 1')


def upgrade():
    op.execute(f'DROP VIEW IF EXISTS {authorizations_view_new.name}')
    op.execute(f'CREATE VIEW {authorizations_view_new.name} AS {authorizations_view_new.sql}')

    permissions_table = table('permissions',
                              column('id', sa.Integer()),
                              column('membership_type_code', sa.String(length=15)),
                              column('org_status_code', sa.String(length=25)),
                              column('actions', sa.String(length=100)))

    # Insert code values
    op.bulk_insert(
        permissions_table,
        [
            {'id': 29, 'membership_type_code': 'ADMIN', 'org_status_code': None,
             'actions': 'edit'},
            {'id': 30, 'membership_type_code': 'ADMIN', 'org_status_code': None,
             'actions': 'view'},
            {'id': 31, 'membership_type_code': 'ADMIN', 'org_status_code': None,
             'actions': 'make-payment'},
            {'id': 32, 'membership_type_code': 'ADMIN', 'org_status_code': None,
             'actions': 'generate-invoice'},

            {'id': 33, 'membership_type_code': 'COORDINATOR', 'org_status_code': None,
             'actions': 'edit'},
            {'id': 34, 'membership_type_code': 'COORDINATOR', 'org_status_code': None,
             'actions': 'view'},
            {'id': 35, 'membership_type_code': 'COORDINATOR', 'org_status_code': None,
             'actions': 'make-payment'},
            {'id': 36, 'membership_type_code': 'COORDINATOR', 'org_status_code': None,
             'actions': 'generate-invoice'},

            {'id': 37, 'membership_type_code': 'USER', 'org_status_code': None,
             'actions': 'edit'},
            {'id': 38, 'membership_type_code': 'USER', 'org_status_code': None,
             'actions': 'view'},
            {'id': 39, 'membership_type_code': 'USER', 'org_status_code': None,
             'actions': 'make-payment'},
            {'id': 40, 'membership_type_code': 'USER', 'org_status_code': None,
             'actions': 'generate-invoice'},

            {'id': 41, 'membership_type_code': 'ADMIN', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'transaction_history'},
            {'id': 42, 'membership_type_code': 'ADMIN', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'transaction_history'},
            {'id': 43, 'membership_type_code': 'ADMIN', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'transaction_history'},
            {'id': 44, 'membership_type_code': 'ADMIN', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'transaction_history'},
            {'id': 45, 'membership_type_code': 'ADMIN', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'transaction_history'},
            {'id': 46, 'membership_type_code': 'ADMIN', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'transaction_history'},

            {'id': 47, 'membership_type_code': 'ADMIN', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'make-payment'},
            {'id': 48, 'membership_type_code': 'ADMIN', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'generate-invoice'},

            {'id': 49, 'membership_type_code': 'SYSTEM', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'make-payment'},
            {'id': 50, 'membership_type_code': 'SYSTEM', 'org_status_code': 'NSF_SUSPENDED',
             'actions': 'generate-invoice'},

            {'id': 51, 'membership_type_code': 'SYSTEM', 'org_status_code': None,
             'actions': 'make-payment'},
            {'id': 52, 'membership_type_code': 'SYSTEM', 'org_status_code': None,
             'actions': 'generate-invoice'},
            {'id': 53, 'membership_type_code': 'SYSTEM', 'org_status_code': None,
             'actions': 'view'},
            {'id': 54, 'membership_type_code': 'SYSTEM', 'org_status_code': None,
             'actions': 'edit'},
        ]
    )
    # Update actions to lower case

    op.execute('update permissions set actions=lower(actions)')


def downgrade():
    op.execute(f'DROP VIEW IF EXISTS {authorizations_view_old.name}')
    op.execute(f'CREATE VIEW {authorizations_view_old.name} AS {authorizations_view_old.sql}')
    op.execute('delete from permissions where id between 29 and 54')
    op.execute('update permissions set actions=upper(actions)')

"""account_payment_settings_changes

Revision ID: de09ab11e3fc
Revises: 0ab62b841b88
Create Date: 2020-04-23 10:40:28.014529

"""
from alembic import op
import sqlalchemy as sa
from auth_api.utils.custom_sql import CustomSql
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = 'de09ab11e3fc'
down_revision = '0ab62b841b88'
branch_labels = None
depends_on = None

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
                                    '   m.status = 1'
                                    '   AND pay.is_active = true; ')


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
                                    '   m.status = 1')

org_type_table = table('org_type',
                       column('code', String),
                       column('desc', String),
                       column('default', Boolean)
                       )


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account_payment_settings', sa.Column('is_active', sa.Boolean(), nullable=True))

    # Update existing table rows
    op.execute('update account_payment_settings set is_active=true')

    # Update view
    op.execute(f'DROP VIEW IF EXISTS {authorizations_view_new.name}')
    op.execute(f'CREATE VIEW {authorizations_view_new.name} AS {authorizations_view_new.sql}')

    # First insert PREMIUM to org_type, Then update all records, then delete IMPLICIT and EXPLICIT from type
    op.bulk_insert(
        org_type_table,
        [
            {'code': 'BASIC', 'desc': 'Basic account', 'default': True}
        ]
    )
    op.execute('update org set type_code=\'BASIC\' where type_code in (\'IMPLICIT\', \'EXPLICIT\')')
    op.execute('delete from org_type where code in (\'IMPLICIT\', \'EXPLICIT\')')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Update view
    op.execute(f'DROP VIEW IF EXISTS {authorizations_view_old.name}')
    op.execute(f'CREATE VIEW {authorizations_view_old.name} AS {authorizations_view_old.sql}')

    op.drop_column('account_payment_settings', 'is_active')
    # ### end Alembic commands ###

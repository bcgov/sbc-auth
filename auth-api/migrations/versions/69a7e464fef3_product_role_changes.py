"""product_role_changes

Revision ID: 69a7e464fef3
Revises: 5053985bdfc6
Create Date: 2021-03-02 12:16:09.152924

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

from auth_api.utils.custom_sql import CustomSql

# revision identifiers, used by Alembic.
revision = '69a7e464fef3'
down_revision = '5053985bdfc6'
branch_labels = None
depends_on = None

authorizations_view = CustomSql('authorizations_view',
                                ' SELECT e.business_identifier,'
                                'e.name AS entity_name,'
                                'e.folio_number,'
                                'e.corp_type_code,'
                                'm.membership_type_code AS org_membership,'
                                'u.keycloak_guid,'
                                'u.id AS user_id,'
                                'o.id AS org_id,'
                                'o.name AS org_name,'
                                'o.status_code,'
                                'o.type_code AS org_type,'
                                'ps.product_code,'
                                'o.bcol_user_id,'
                                'o.bcol_account_id'
                                ' FROM memberships m '
                                'LEFT JOIN orgs o ON m.org_id = o.id '
                                'LEFT JOIN users u ON u.id = m.user_id '
                                'LEFT JOIN affiliations a ON o.id = a.org_id '
                                'LEFT JOIN entities e ON e.id = a.entity_id '
                                'LEFT JOIN product_subscriptions ps ON ps.org_id = o.id '
                                'WHERE m.status = 1;')


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    permissions_table = table('permissions',
                              column('id', sa.Integer()),
                              column('membership_type_code', sa.String(length=15)),
                              column('org_status_code', sa.String(length=25)),
                              column('actions', sa.String(length=100)))

    # Insert code values
    op.bulk_insert(
        permissions_table,
        [
            {'id': 68, 'membership_type_code': 'ADMIN', 'org_status_code': None, 'actions': 'ppr'},
            {'id': 69, 'membership_type_code': 'COORDINATOR', 'org_status_code': None, 'actions': 'ppr'},
            {'id': 70, 'membership_type_code': 'USER', 'org_status_code': None, 'actions': 'ppr'}
        ]
    )

    op.execute(f'DROP VIEW IF EXISTS {authorizations_view.name}')
    op.execute(f'CREATE VIEW {authorizations_view.name} AS {authorizations_view.sql}')

    op.execute('delete from product_subscription_roles')
    op.execute('delete from product_role_codes')
    op.drop_table('product_subscription_roles')
    op.drop_table('product_subscription_roles_version')

    op.drop_table('product_role_codes')

    # Create PPR product for PREMIUM accounts.
    # Delete PPR subscription from all accounts.
    op.execute("delete from product_subscriptions where product_code='PPR'")

    conn = op.get_bind()
    res = conn.execute("select id from orgs where type_code='PREMIUM' ")
    orgs = res.fetchall()

    for org in orgs:
        org_id = org[0]
        # Update payment method in invoice
        op.execute(f"insert into product_subscriptions(product_code, org_id) values ('PPR', {org_id})")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product_subscription_roles_version',
                    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('product_subscription_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('product_role_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('created_by_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('modified', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('modified_by_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', 'transaction_id', name='product_subscription_role_version_pkey')
                    )
    op.create_index('ix_product_subscription_roles_version_transaction_id', 'product_subscription_roles_version',
                    ['transaction_id'], unique=False)
    op.create_index('ix_product_subscription_roles_version_operation_type', 'product_subscription_roles_version',
                    ['operation_type'], unique=False)
    op.create_index('ix_product_subscription_roles_version_end_transaction_id', 'product_subscription_roles_version',
                    ['end_transaction_id'], unique=False)
    op.create_table('product_role_codes',
                    sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('modified', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('code', sa.VARCHAR(length=15), autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
                    sa.Column('product_code', sa.VARCHAR(length=15), autoincrement=False, nullable=False),
                    sa.Column('created_by_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('modified_by_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'],
                                            name='product_role_code_created_by_id_fkey'),
                    sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'],
                                            name='product_role_code_modified_by_id_fkey'),
                    sa.ForeignKeyConstraint(['product_code'], ['product_codes.code'],
                                            name='product_role_code_product_codes_fkey'),
                    sa.PrimaryKeyConstraint('id', name='product_role_codes_pkey')
                    )
    op.create_table('product_subscription_roles',
                    sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('modified', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('product_subscription_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('product_role_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('created_by_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('modified_by_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='product_role_created_by_id_fkey'),
                    sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], name='product_role_modified_by_id_fkey'),
                    sa.ForeignKeyConstraint(['product_role_id'], ['product_role_codes.id'],
                                            name='product_role_product_role_id_fkey'),
                    sa.ForeignKeyConstraint(['product_subscription_id'], ['product_subscriptions.id'],
                                            name='product_role_product_subscription_id_fkey'),
                    sa.PrimaryKeyConstraint('id', name='product_role_pkey')
                    )

    op.create_index('ix_product_role_codes_code', 'product_role_codes', ['code'], unique=False)
    op.execute('delete from permissions where id in (68, 69, 70)')
    # ### end Alembic commands ###

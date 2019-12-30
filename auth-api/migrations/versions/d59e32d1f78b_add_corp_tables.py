"""add corp tables

Revision ID: d59e32d1f78b
Revises: 93ba1db65ed3
Create Date: 2019-12-23 11:36:43.202374

"""
from alembic import op
import sqlalchemy as sa
from auth_api.utils.custom_sql import CustomSql

# revision identifiers, used by Alembic.
revision = 'd59e32d1f78b'
down_revision = '93ba1db65ed3'
branch_labels = None
depends_on = None

authorizations_view = CustomSql('authorizations_view',
                                ' SELECT e.business_identifier, e.name AS entity_name,e.corp_type_code as corp_type_code, m.membership_type_code AS org_membership, u.keycloak_guid, u.id AS user_id, o.id AS org_id, o.type_code AS org_type'
                                ' FROM (( ( membership m left join org o on m.org_id = o.id ) '
                                'left join "user" u on u.id = m.user_id ) '
                                'left join affiliation a on o.id = a.org_id) '
                                'left join entity e on e.id = a.entity_id '
                                'where m.status =1 ')


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    corp_type_table = op.create_table('corp_type',
                                      sa.Column('created', sa.DateTime(), nullable=True),
                                      sa.Column('modified', sa.DateTime(), nullable=True),
                                      sa.Column('code', sa.String(length=15), nullable=False),
                                      sa.Column('desc', sa.String(length=100), nullable=True),
                                      sa.Column('default', sa.Boolean(), nullable=False),
                                      sa.Column('created_by_id', sa.Integer(), nullable=True),
                                      sa.Column('modified_by_id', sa.Integer(), nullable=True),
                                      sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ),
                                      sa.ForeignKeyConstraint(['modified_by_id'], ['user.id'], ),
                                      sa.PrimaryKeyConstraint('code')
                                      )

    op.add_column('entity', sa.Column('corp_type_code', sa.String(length=15), nullable=True))
    # op.create_foreign_key('entity_corp_type_fkey', ['entity.corp_type_code'], ['corp_type.code'])
    op.create_foreign_key('entity_corp_type_fkey', 'entity', 'corp_type', ['corp_type_code'], ['code'])

    # Insert code values
    op.bulk_insert(
        corp_type_table,
        [
            {'code': 'CP', 'desc': 'Cooperatives', 'default': True},
            {'code': 'BC', 'desc': 'BC Companies', 'default': False}
        ]
    )

    # Update all existing user records to active
    op.execute('update "entity" set corp_type_code=\'CP\' where business_number like \'CP%\'')
    op.execute('update "entity" set corp_type_code=\'BC\' where business_number like \'BC%\'')

    op.execute(f'DROP VIEW IF EXISTS {authorizations_view.name}')
    op.execute(f'CREATE VIEW {authorizations_view.name} AS {authorizations_view.sql}')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(f'DROP VIEW {authorizations_view.name}')
    op.drop_constraint('entity_corp_type_fkey', 'entity', type_='foreignkey')
    op.drop_column('entity', 'corp_type_code')
    op.drop_table('corp_type')

    # ### end Alembic commands ###

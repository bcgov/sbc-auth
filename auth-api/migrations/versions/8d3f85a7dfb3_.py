"""empty message

Revision ID: 8d3f85a7dfb3
Revises: 1f64b1786ecc
Create Date: 2019-05-03 16:00:58.894118

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8d3f85a7dfb3'
down_revision = '1f64b1786ecc'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user', 'roles',
                    existing_type=sa.VARCHAR(length=1000),
                    nullable=True)
    op.alter_column('user', 'username',
                    existing_type=sa.VARCHAR(length=100),
                    nullable=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=False)
    op.create_table(
        'user_type',
        sa.Column('user_type_code', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
        sa.Column('user_type_name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('full_desc', sa.VARCHAR(length=250), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('user_type_code', name='user_type_pkey'),
        postgresql_ignore_search_path=False
    )

    op.create_table(
        'users',
        sa.Column('user_id', sa.INTEGER(), server_default=sa.text("nextval('users_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('username', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column('passwd', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column('firstname', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column('lastname', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
        sa.Column('display_name', sa.VARCHAR(length=254), autoincrement=False, nullable=True),
        sa.Column('email', sa.VARCHAR(length=254), autoincrement=False, nullable=True),
        sa.Column('user_source', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
        sa.Column('user_type_code', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
        sa.Column('sub', sa.VARCHAR(length=36), autoincrement=False, nullable=True, comment='From token. Keycloak user id.'),
        sa.Column('iss', sa.VARCHAR(length=1024), autoincrement=False, nullable=True, comment='From token. Keycloak base URL.'),
        sa.Column('creation_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['user_type_code'], ['user_type.user_type_code'], name='users_user_type_fkey'),
        sa.PrimaryKeyConstraint('user_id', name='users_pkey'),
        sa.UniqueConstraint('sub', name='users_sub_key'),
        sa.UniqueConstraint('username', name='username'),
        postgresql_ignore_search_path=False
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    op.create_table(
        'action',
        sa.Column('action_code', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('action_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.Column('action_type', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('path', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('action_code', name='action_pkey'),
        postgresql_ignore_search_path=False
    )
    op.create_table(
        'action_log',
        sa.Column('log_id', sa.INTEGER(), server_default=sa.text("nextval('log_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('action_code', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
        sa.Column('target_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('target_type', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('action_date', sa.DATE(), autoincrement=False, nullable=False),
        sa.Column('memo', sa.VARCHAR(length=250), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['action_code'], ['action.action_code'], name='action_log_action_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name='action_log_user_fkey'),
        sa.PrimaryKeyConstraint('log_id', name='log_pkey')
    )
    op.create_table(
        'affiliation_business',
        sa.Column('business_id', sa.INTEGER(), server_default=sa.text("nextval('business_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('corp_num', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
        sa.Column('corp_type', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('business_id', name='affiliation_business_pkey'),
        postgresql_ignore_search_path=False
    )
    op.create_table(
        'affiliation_status',
        sa.Column('status_code', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
        sa.Column('status_name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('status_code', name='affiliation_status_pkey'),
        postgresql_ignore_search_path=False
    )

    op.create_table(
        'affiliation',
        sa.Column('affiliation_id', sa.INTEGER(), server_default=sa.text("nextval('affiliation_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('affiliation_status_code', sa.VARCHAR(length=5), autoincrement=False, nullable=False),
        sa.Column('business_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('effective_start_date', sa.DATE(), autoincrement=False, nullable=False),
        sa.Column('effective_end_date', sa.DATE(), autoincrement=False, nullable=True),
        sa.Column('created_by_userid', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('creation_date', sa.DATE(), autoincrement=False, nullable=True),
        sa.Column('modified_by_userid', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('last_access_date', sa.DATE(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['affiliation_status_code'], ['affiliation_status.status_code'], name='affiliation_affiliation_status_fkey'),
        sa.ForeignKeyConstraint(['business_id'], ['affiliation_business.business_id'], name='affiliation_business_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name='affiliation_user_fkey'),
        sa.PrimaryKeyConstraint('affiliation_id', name='affiliation_pkey')
    )


def downgrade():
    op.drop_table('affiliation')
    op.drop_table('user_type')
    op.drop_table('affiliation_status')
    op.drop_table('affiliation_business')
    op.drop_table('action_log')
    op.drop_table('action')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.alter_column('user', 'username',
                    existing_type=sa.VARCHAR(length=100),
                    nullable=False)
    op.alter_column('user', 'roles',
                    existing_type=sa.VARCHAR(length=1000),
                    nullable=False)

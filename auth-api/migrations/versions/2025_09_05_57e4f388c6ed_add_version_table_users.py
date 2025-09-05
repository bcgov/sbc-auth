"""Add in version table for users

Revision ID: 57e4f388c6ed
Revises: 8173f0949f2e
Create Date: 2025-09-05 11:00:30.683506

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '57e4f388c6ed'
down_revision = '8173f0949f2e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users_history',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('username', sa.String(length=100), autoincrement=False, nullable=True),
    sa.Column('first_name', sa.String(length=200), autoincrement=False, nullable=True),
    sa.Column('last_name', sa.String(length=200), autoincrement=False, nullable=True),
    sa.Column('email', sa.String(length=200), autoincrement=False, nullable=True),
    sa.Column('keycloak_guid', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('is_terms_of_use_accepted', sa.Boolean(), autoincrement=False, nullable=True),
    sa.Column('terms_of_use_accepted_version', sa.String(length=10), autoincrement=False, nullable=True),
    sa.Column('type', sa.String(length=200), autoincrement=False, nullable=True),
    sa.Column('status', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('idp_userid', sa.String(length=256), autoincrement=False, nullable=True),
    sa.Column('login_source', sa.String(length=200), autoincrement=False, nullable=True),
    sa.Column('login_time', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('verified', sa.Boolean(), autoincrement=False, nullable=True),
    sa.Column('created', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('modified', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('created_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('modified_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('version', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('changed', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['users_history.id'], ),
    sa.ForeignKeyConstraint(['modified_by_id'], ['users_history.id'], ),
    sa.ForeignKeyConstraint(['status'], ['user_status_codes.id'], ),
    sa.ForeignKeyConstraint(['terms_of_use_accepted_version'], ['documents.version_id'], ),
    sa.PrimaryKeyConstraint('id', 'version'),
    sqlite_autoincrement=True
    )
    with op.batch_alter_table('users_history', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_history_email'), ['email'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_history_first_name'), ['first_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_history_idp_userid'), ['idp_userid'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_history_last_name'), ['last_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_history_username'), ['username'], unique=False)
    
    op.execute(
        """
               update users set version =
                    (select coalesce(
                        (select count(transaction_id) as version
                            from users_version
                        where 
                            users.id = users_version.id
                        group by
                            id
                    ), 1));
               """
    )

    op.execute(
        """
        with subquery as (
            select 
                uv.id,
                username, 
                first_name, 
                last_name, 
                email, 
                keycloak_guid, 
                created, 
                modified, 
                created_by_id,
                modified_by_id,
                is_terms_of_use_accepted,
                terms_of_use_accepted_version,
                type,
                status,
                idp_userid,
                login_source,
                login_time,
                verified,
                t.issued_at as changed, 
                COALESCE(ROW_NUMBER() OVER (PARTITION BY uv.id ORDER BY uv.transaction_id ASC), 1) as version
            from 
                users_version uv 
            left join 
               transaction t on uv.transaction_id = t.id
        ),
        max_versions as (
            select 
                id,
                max(version) as max_version
            from 
               subquery sq
            group by id
        )
               
        insert into 
                    users_history (id, username, first_name, last_name, email, keycloak_guid, created, modified, created_by_id, modified_by_id, is_terms_of_use_accepted, terms_of_use_accepted_version, type, status, idp_userid, login_source, login_time, verified, changed, version) 
        select 
            sq.id, sq.username, sq.first_name, sq.last_name, sq.email, sq.keycloak_guid, sq.created, sq.modified, sq.created_by_id, sq.modified_by_id, sq.is_terms_of_use_accepted, sq.terms_of_use_accepted_version, sq.type, sq.status, sq.idp_userid, sq.login_source, sq.login_time, sq.verified, sq.changed, sq.version
        from 
            subquery sq
        left join 
            max_versions mv on mv.id = sq.id
        where
               sq.version != mv.max_version;
               """
    )

    op.drop_table('users_version')

def downgrade():
    op.create_table('users_version',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('username', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('first_name', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('last_name', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('keycloak_guid', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('is_terms_of_use_accepted', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('terms_of_use_accepted_version', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    sa.Column('type', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('status', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('idp_userid', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('login_source', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('login_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('created_by_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
    sa.Column('verified', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', 'transaction_id', name='user_version_pkey')
    )
    with op.batch_alter_table('users_version', schema=None) as batch_op:
        batch_op.create_index('ix_users_version_username', ['username'], unique=False)
        batch_op.create_index('ix_users_version_transaction_id', ['transaction_id'], unique=False)
        batch_op.create_index('ix_users_version_operation_type', ['operation_type'], unique=False)
        batch_op.create_index('ix_users_version_last_name', ['last_name'], unique=False)
        batch_op.create_index('ix_users_version_idp_userid', ['idp_userid'], unique=False)
        batch_op.create_index('ix_users_version_first_name', ['first_name'], unique=False)
        batch_op.create_index('ix_users_version_end_transaction_id', ['end_transaction_id'], unique=False)
        batch_op.create_index('ix_users_version_email', ['email'], unique=False)

    op.drop_table('users_history')

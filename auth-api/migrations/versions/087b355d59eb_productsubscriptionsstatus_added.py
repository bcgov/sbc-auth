"""ProductSubscriptionsStatus added

Revision ID: 087b355d59eb
Revises: 2d71e7d7cc18
Create Date: 2021-03-31 06:46:14.391613

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table
from sqlalchemy import Boolean, String

# revision identifiers, used by Alembic.
revision = '087b355d59eb'
down_revision = '2d71e7d7cc18'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('product_codes', sa.Column('default_subscription_status', sa.String(length=30), nullable=False,
                                             server_default='ACTIVE'))

    op.create_table('product_subscriptions_statuses',
                    sa.Column('created', sa.DateTime(), nullable=True),
                    sa.Column('modified', sa.DateTime(), nullable=True),
                    sa.Column('code', sa.String(length=30), nullable=False),
                    sa.Column('description', sa.String(length=100), nullable=True),
                    sa.Column('default', sa.Boolean(), nullable=False),
                    sa.Column('created_by_id', sa.Integer(), nullable=True),
                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
                    sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('code')
                    )

    # add master data

    product_subscriptions_statuses_table = table('product_subscriptions_statuses',
                                                 column('code', String),
                                                 column('description', String),
                                                 column('default', Boolean)
                                                 )
    op.bulk_insert(
        product_subscriptions_statuses_table,
        [
            {'code': 'REJECTED', 'description': 'Status for a rejected account',
             'default': False},
            {'code': 'ACTIVE', 'description': 'Status for a active account',
             'default': True},
            {'code': 'PENDING_STAFF_REVIEW', 'description': 'Status for a PENDING_STAFF_REVIEW account',
             'default': False},
            {'code': 'INACTIVE', 'description': 'Status for a inactive account',
             'default': False}
        ]
    )

    op.add_column('product_subscriptions',
                  sa.Column('status_code', sa.String(length=30), nullable=False, server_default='ACTIVE'))
    op.create_foreign_key('product_subscriptions_status_fk', 'product_subscriptions', 'product_subscriptions_statuses',
                          ['status_code'], ['code'])
    op.add_column('product_subscriptions_version',
                  sa.Column('status_code', sa.String(length=30), autoincrement=False, nullable=True))
    op.create_foreign_key('product_codes_status_fk', 'product_codes', 'product_subscriptions_statuses',
                          ['default_subscription_status'], ['code'])
    # ### end Alembic commands ###

    # update vital stats data

    # Update existing table rows
    op.execute("update product_codes set description='Wills Registry',"
               "default_subscription_status='PENDING_STAFF_REVIEW' where "
               "code='VS'")


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product_subscriptions_version', 'status_code')
    op.drop_constraint('product_subscriptions_status_fk', 'product_subscriptions', type_='foreignkey')
    op.drop_constraint('product_codes_status_fk', 'product_codes', type_='foreignkey')
    op.drop_column('product_subscriptions', 'status_code')
    op.drop_table('product_subscriptions_statuses')
    op.drop_column('product_codes', 'default_subscription_status')
    # ### end Alembic commands ###

"""Insert org type and status codes

Revision ID: 4150773f899f
Revises: b2dda0178918
Create Date: 2019-08-14 11:43:42.765706

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '4150773f899f'
down_revision = 'b2dda0178918'
branch_labels = None
depends_on = None


def upgrade():
    # Insert codes and descriptions for organization types

    org_type_table = table('org_type',
                           column('code', String),
                           column('desc', String),
                           column('default', Boolean)
                           )

    op.bulk_insert(
        org_type_table,
        [
            {'code': 'IMPLICIT', 'desc': 'Implicit organization for internal user only', 'default': True},
            {'code': 'EXPLICIT', 'desc': 'Explicity named organization that can have multiple members', 'default': False}
        ]
    )

    # Insert codes and descriptions for organization status
    org_status_table = table('org_status',
                             column('code', String),
                             column('desc', String),
                             column('default', Boolean)
                             )
    op.bulk_insert(
        org_status_table,
        [
            {'code': 'ACTIVE', 'desc': 'Status for an implicit org, or an explicit org that has been verified', 'default': True},
            {'code': 'PENDING', 'desc': 'Status for an explicit, named org while awaiting verification', 'default': False},
            {'code': 'INACTIVE', 'desc': 'Status for an organization that is no longer active', 'default': False}
        ]
    )

    # Insert codes and descriptions for payment types
    payment_types_table = table('payment_type',
                               column('code', String),
                               column('desc', String),
                               column('default', Boolean)
                               )
    op.bulk_insert(
        payment_types_table,
        [
            {'code': 'CC', 'desc': 'Credit Card', 'default': True}
        ]
    )


def downgrade():
    op.execute('DELETE FROM org_type WHERE code = \'IMPLICIT\';')
    op.execute('DELETE FROM org_type WHERE code = \'EXPLICIT\';')
    op.execute('DELETE FROM org_status WHERE code = \'ACTIVE\';')
    op.execute('DELETE FROM org_status WHERE code = \'PENDING\';')
    op.execute('DELETE FROM org_status WHERE code = \'INACTIVE\';')
    op.execute('DELETE FROM payment_type WHERE code = \'CC\';')

"""removed PENDING_AFFIDAVIT_REVIEW 

Revision ID: 2d71e7d7cc18
Revises: 4d47b5569629
Create Date: 2021-03-15 14:17:11.066811

"""

from alembic import op
from sqlalchemy import Boolean, String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '2d71e7d7cc18'
down_revision = '4d47b5569629'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("update orgs set status_code = 'PENDING_STAFF_REVIEW' where status_code='PENDING_AFFIDAVIT_REVIEW'")
    op.execute("delete from org_statuses where code='PENDING_AFFIDAVIT_REVIEW'")


def downgrade():
    org_status_table = table('org_statuses',
                             column('code', String),
                             column('description', String),
                             column('default', Boolean)
                             )
    op.bulk_insert(
        org_status_table,
        [
            {'code': 'PENDING_AFFIDAVIT_REVIEW', 'description': 'Status for pending affidavit review',
             'default': False}
        ]
    )
    # for now , this will work since there is no other staff review
    op.execute("update orgs set status_code = 'PENDING_AFFIDAVIT_REVIEW' where status_code='PENDING_STAFF_REVIEW'")

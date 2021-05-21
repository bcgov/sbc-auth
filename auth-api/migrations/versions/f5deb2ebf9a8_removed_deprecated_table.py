"""removed deprecated table 

Revision ID: f5deb2ebf9a8
Revises: 2eb11ab005d3
Create Date: 2021-05-07 13:44:06.057924

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'f5deb2ebf9a8'
down_revision = '2eb11ab005d3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('DROP table IF EXISTS account_payment_settings ')
    op.execute('DROP table IF EXISTS account_payment_settings_version ')


def downgrade():
    # do not add these table back.deprecated ones#
    pass

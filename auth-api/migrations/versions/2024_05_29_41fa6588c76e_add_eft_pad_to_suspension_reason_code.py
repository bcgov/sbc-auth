"""Add EFT PAD to suspension_reason_code

Revision ID: 41fa6588c76e
Revises: 1e4b6359f470
Create Date: 2024-05-29 10:36:53.016963

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41fa6588c76e'
down_revision = '1e4b6359f470'
branch_labels = None
depends_on = None


def upgrade():
        op.execute("INSERT INTO suspension_reason_codes "
                "(code, description,\"default\") "
                "VALUES "
                "('EFT_NSF', 'EFT NSF', false)")
        op.execute("INSERT INTO suspension_reason_codes "
            "(code, description,\"default\") "
            "VALUES "
            "('PAD_NSF', 'PAD NSF', false)")
        op.execute("update orgs set suspension_reason_code = 'PAD_NSF' where status_code = 'NSF_SUSPENDED'")

def downgrade():
        op.execute("DELETE FROM suspension_reason_codes WHERE code in ('EFT_NSF', 'PAD_NSF')")
        op.execute("update orgs set suspension_reason_code = NULL where status_code = 'NSF_SUSPENDED'")

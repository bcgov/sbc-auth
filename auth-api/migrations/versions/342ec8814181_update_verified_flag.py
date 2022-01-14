"""update_verified_flag

Revision ID: 342ec8814181
Revises: 9f3450623765
Create Date: 2022-01-13 16:12:10.256555

"""
from typing import List

from alembic import op

from auth_api.models import Affidavit

# revision identifiers, used by Alembic.
revision = '342ec8814181'
down_revision = '9f3450623765'
branch_labels = None
depends_on = None


def upgrade():
    # Find approved BCeID affidavit users.
    conn = op.get_bind()
    affidavits: List[Affidavit] = conn.execute("select * from affidavits where status_code='APPROVED' ").fetchall()
    for affidavit in affidavits:
        op.execute(f"update users set verified=true where id = {affidavit.user_id};")

    op.execute("update users set verified=true where login_source='BCSC'")


def downgrade():
    pass

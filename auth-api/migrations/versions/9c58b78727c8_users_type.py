"""users_type

Revision ID: 9c58b78727c8
Revises: 5397c5a5b0ca
Create Date: 2021-06-29 14:51:52.950816

"""

from alembic import op
from sqlalchemy import text
import sqlalchemy as sa
from auth_api.models import User
from auth_api.utils.enums import LoginSource
from auth_api.utils.roles import Role
from typing import List


# revision identifiers, used by Alembic.
revision = "9c58b78727c8"
down_revision = "5397c5a5b0ca"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    user_res = conn.execute(text("SELECT * FROM users WHERE coalesce(TRIM(type), '') = ''"))
    users: List[User] = user_res.fetchall()

    for user in users:
        login_source = user.login_source
        if user.login_source in [LoginSource.BCEID.value, LoginSource.BCSC.value]:
            user_type = Role.PUBLIC_USER.name
        elif user.login_source == LoginSource.STAFF.value:
            user_type = Role.STAFF.name

        # update user.
        op.execute(f"update users set type='{user_type}', login_source='{login_source}' where id={user.id}")


def downgrade():
    pass

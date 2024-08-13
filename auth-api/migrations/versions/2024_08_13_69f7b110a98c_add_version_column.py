"""add version column

Revision ID: 69f7b110a98c
Revises: af98933abe93
Create Date: 2024-08-13 09:55:11.041391

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "69f7b110a98c"
down_revision = "af98933abe93"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("account_login_options", schema=None) as batch_op:
        batch_op.add_column(sa.Column("version", sa.Integer(), nullable=False, server_default="1"))

    with op.batch_alter_table("affidavits", schema=None) as batch_op:
        batch_op.add_column(sa.Column("version", sa.Integer(), nullable=False, server_default="1"))

    with op.batch_alter_table("contact_links", schema=None) as batch_op:
        batch_op.add_column(sa.Column("version", sa.Integer(), nullable=False, server_default="1"))

    with op.batch_alter_table("contacts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("version", sa.Integer(), nullable=False, server_default="1"))

    with op.batch_alter_table("memberships", schema=None) as batch_op:
        batch_op.add_column(sa.Column("version", sa.Integer(), nullable=False, server_default="1"))

    with op.batch_alter_table("org_settings", schema=None) as batch_op:
        batch_op.add_column(sa.Column("version", sa.Integer(), nullable=False, server_default="1"))

    with op.batch_alter_table("orgs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("version", sa.Integer(), nullable=False, server_default="1"))

    with op.batch_alter_table("product_subscriptions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("version", sa.Integer(), nullable=False, server_default="1"))

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("version", sa.Integer(), nullable=False, server_default="1"))


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("version")

    with op.batch_alter_table("product_subscriptions", schema=None) as batch_op:
        batch_op.drop_column("version")

    with op.batch_alter_table("orgs", schema=None) as batch_op:
        batch_op.drop_column("version")

    with op.batch_alter_table("org_settings", schema=None) as batch_op:
        batch_op.drop_column("version")

    with op.batch_alter_table("memberships", schema=None) as batch_op:
        batch_op.drop_column("version")

    with op.batch_alter_table("contacts", schema=None) as batch_op:
        batch_op.drop_column("version")

    with op.batch_alter_table("contact_links", schema=None) as batch_op:
        batch_op.drop_column("version")

    with op.batch_alter_table("affidavits", schema=None) as batch_op:
        batch_op.drop_column("version")

    with op.batch_alter_table("account_login_options", schema=None) as batch_op:
        batch_op.drop_column("version")

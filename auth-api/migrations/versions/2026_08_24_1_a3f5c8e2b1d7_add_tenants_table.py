"""add_tenants_table

Revision ID: a3f5c8e2b1d7
Revises: bff7f0c3bac4
Create Date: 2026-08-24 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a3f5c8e2b1d7'
down_revision = 'e9e8922667a4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('tenants',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tenant_key', sa.String(length=50), nullable=False,
              comment="Immutable public identifier, lowercase snake (e.g. 'wills', 'min_agri')"),
    sa.Column('name', sa.String(length=250), nullable=False,
              comment="Display name (e.g. 'Ministry of Agriculture')"),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('admin_org_id', sa.Integer(), nullable=True,
              comment='Auto-provisioned org whose ADMIN members are the tenant administrators'),
    sa.Column('status', sa.String(length=20), nullable=False, server_default='ACTIVE',
              comment='ACTIVE or INACTIVE'),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('modified_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['admin_org_id'], ['orgs.id'], ),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tenant_key', name='uq_tenants_tenant_key')
    )
    # UNIQUE constraint above creates an implicit btree index on tenant_key,
    # which serves lookup queries — no additional index needed on this column.

    with op.batch_alter_table('product_codes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_key', sa.String(length=50), nullable=True,
                                       comment='Owning tenant; nullable during rollout'))
        batch_op.create_foreign_key('fk_product_codes_tenant_key', 'tenants',
                                    ['tenant_key'], ['tenant_key'])
        batch_op.create_index(batch_op.f('ix_product_codes_tenant_key'),
                              ['tenant_key'], unique=False)

    # Seed TENANT org type used as the auto-provisioned admin org's type_code.
    op.execute(
        "INSERT INTO org_types (code, description, \"default\") "
        "VALUES ('TENANT', 'Tenant Admin Org', false) "
        "ON CONFLICT (code) DO NOTHING"
    )


def downgrade():
    op.execute("DELETE FROM org_types WHERE code = 'TENANT'")

    with op.batch_alter_table('product_codes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_product_codes_tenant_key'))
        batch_op.drop_constraint('fk_product_codes_tenant_key', type_='foreignkey')
        batch_op.drop_column('tenant_key')

    op.drop_table('tenants')

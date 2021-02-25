"""create suspend_account_reason_codes

Revision ID: 79629d53ebdf
Revises: 8260fac9943d
Create Date: 2021-02-25 12:50:14.591121

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79629d53ebdf'
down_revision = '8260fac9943d'
branch_labels = None
depends_on = None


def upgrade():
    suspend_account_reason_codes = op.create_table('suspend_account_reason_codes',
                                                    sa.Column('created', sa.DateTime(), nullable=True),
                                                    sa.Column('modified', sa.DateTime(), nullable=True),
                                                    sa.Column('id', sa.Integer(), nullable=False),
                                                    sa.Column('code', sa.String(length=25), nullable=True),
                                                    sa.Column('description', sa.String(length=100), nullable=True),
                                                    sa.Column('created_by_id', sa.Integer(), nullable=True),
                                                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                                                    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
                                                    sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
                                                    sa.PrimaryKeyConstraint('id')
                                                    )

    # Insert code values
    op.bulk_insert(
        suspend_account_reason_codes,
        [
            {'id': 1, 'code': 'CHANGE', 'description': 'Account Ownership Change'},
            {'id': 2, 'code': 'DISPUTE', 'description': 'Account Ownership Dispute'},
            {'id': 3, 'code': 'COURTORDER', 'description': 'Court Order'},
            {'id': 4, 'code': 'FRAUDULENT', 'description': 'Fraudulent Activity'},
            {'id': 5, 'code': 'OTHER', 'description': 'Other'}
        ]
    )


def downgrade():
    op.drop_table('suspend_account_reason_codes')

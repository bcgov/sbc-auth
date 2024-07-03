"""add_business_and_government_flags_and_remove_rows

Revision ID: 1e4b6359f470
Revises: b3a741249edc
Create Date: 2024-05-23 10:18:59.135894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e4b6359f470'
down_revision = 'b3a741249edc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('business_type_codes', sa.Column('is_government_agency', sa.Boolean(), nullable=True))
    op.add_column('business_type_codes', sa.Column('is_business', sa.Boolean(), nullable=True))

    mapping = [
        ("BIZ", False, True),
        ("BIZAC", False, True),
        ("BIZEL", False, True),
        ("BIZGA", False, True),
        ("BIZGE", False, True),
        ("BSPLY", False, True),
        ("CAR", False, True),
        ("CAREQ", False, True),
        ("CON", False, True),
        ("EDUC", False, True),
        ("EXPLR", False, True),
        ("FINBA", False, True),
        ("FINCO", False, True),
        ("FINCU", False, True),
        ("FINIC", False, True),
        ("FINLE", False, True),
        ("FINTR", False, True),
        ("FIRNA", False, True),
        ("FOR", False, True),
        ("GOVA", True, False),
        ("GOVAA", True, False),
        ("GOVCC", True, False),
        ("GOVD", True, False),
        ("GOVF", True, False),
        ("GOVGA", True, False),
        ("GOVL", True, False),
        ("GOVLT", True, False),
        ("GOVM", True, False),
        ("GOVOP", True, False),
        ("GOVP", True, False),
        ("GOVR", True, False),
        ("GOVSR", True, False),
        ("HLTH", True, False),
        ("INSUR", False, True),
        ("INTRN", False, False),
        ("LAW", False, True),
        ("LAWNP", False, True),
        ("LDB", False, True),
        ("LDBC", False, False),
        ("MAR", False, True),
        ("OTHCC", False, True),
        ("OTHCR", False, True),
        ("OTHER", True, True),
        ("OTHNE", False, True),
        ("OTHUN", False, True),
        ("PILOT", False, False),
        ("REAL", False, True),
        ("REALA", False, True),
        ("REALB", False, True),
        ("RESRC", False, True),
        ("SES", True, False),
        ("SURV", False, True),
        ("TSC", False, True)
    ]

    for code, is_government_agency, is_business in mapping:
        op.execute(f"UPDATE business_type_codes SET is_government_agency = '{is_government_agency}', is_business = '{is_business}' WHERE code = '{code}'")

    # Delete rows that need to be removed
    codes_to_remove = [
        "PILOT",  # HRV
        "INTRN",  # Internal BCOL account
        "GOVOP",   # Other provincial govt. ministry
        "GOVR"   # Registries who participate in BCOL 
    ]

    for code in codes_to_remove:
        op.execute(f"DELETE FROM business_type_codes WHERE code = '{code}'")


def downgrade():
    # Remove the columns in the downgrade
    op.drop_column('business_type_codes', 'is_government_agency')
    op.drop_column('business_type_codes', 'is_business')

    # Reinsert the removed rows
    op.bulk_insert(
        sa.table('business_type_codes',
                 sa.column('code', sa.String(length=15)),
                 sa.column('description', sa.String(length=100)),
                 sa.column('default', sa.Boolean())
                 ),
        [
            {"code": "PILOT", "description": "HRV", "default": False},
            {"code": "INTRN", "description": "INTERNAL BCOL ACCOUNT", "default": False},
            {"code": "GOVOP", "description": "OTHER PROVINCIAL GOVT. MINISTRY", "default": False},
            {"code": "GOVR", "description": "REGISTRIES WHO PARTICIPATE IN BCOL", "default": False}
        ]
    )
    
    # Remove the new rows added in the upgrade
    codes_added = [
        "BIZ", "BIZAC", "BIZEL", "BIZGA", "BIZGE", "BSPLY", "CAR", "CAREQ", "CON", "EDUC", "EXPLR", "FINBA", "FINCO",
        "FINCU", "FINIC", "FINLE", "FINTR", "FIRNA", "FOR", "GOVA", "GOVAA", "GOVCC", "GOVD", "GOVF", "GOVGA", "GOVL",
        "GOVLT", "GOVM", "GOVOP", "GOVP", "GOVR", "GOVSR", "HLTH", "INSUR", "LAW", "LAWNP", "LDB", "LDBC", "MAR",
        "OTHCC", "OTHCR", "OTHER", "OTHNE", "OTHUN", "REAL", "REALA", "REALB", "RESRC", "SES", "SURV", "TSC"
    ]

    for code in codes_added:
        op.execute(f"DELETE FROM business_type_codes WHERE code = '{code}'")

"""26014-permissions-updates

Revision ID: 2ef3f0be3759
Revises: 7f48833011c3
Create Date: 2025-02-27 07:39:21.022247

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ef3f0be3759'
down_revision = '7f48833011c3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'change_address');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'change_org_name');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'change_role');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'edit_request_product_package');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'deactivate_account');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'generate_invoice');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'invite_members');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'make_payment');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'manage_statements');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'remove_business');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'reset_otp');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'reset_password');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'transaction_history');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'view_activitylog');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'view_address');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'view_admin_contact');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'view_auth_options');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'view_request_product_package');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'view_user_loginsource');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'edit_user');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'view_business_registry_dashboard');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'view_launch_titles');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('STAFF', 'view_continuation_authorization_reviews');""")

    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'change_org_name');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'change_role');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'manage_statements');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'remove_business');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'reset_otp');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'reset_password');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'transaction_history');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'view_activitylog');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'view_address');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'view_admin_contact');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'view_auth_options');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'view_request_product_package');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('CONTACT_CENTRE_STAFF', 'view_user_loginsource');""")

    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'change_org_name');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'change_role');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'manage_statements');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'remove_business');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'reset_otp');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'reset_password');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'transaction_history');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'view_activitylog');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'view_address');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'view_admin_contact');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'view_auth_options');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'view_request_product_package');""")
    op.execute("""INSERT INTO public.permissions (membership_type_code, actions) VALUES ('MAXIMUS_STAFF', 'view_user_loginsource');""")


def downgrade():
    op.execute("delete from permissions where membership_type_code = 'STAFF'")
    op.execute("delete from permissions where membership_type_code = 'CONTACT_CENTRE_STAFF'")
    op.execute("delete from permissions where membership_type_code = 'MAXIMUS_STAFF'")

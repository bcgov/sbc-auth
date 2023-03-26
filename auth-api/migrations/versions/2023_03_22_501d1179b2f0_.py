"""Add in MHR and PPR products for BCOL orgs, also add the roles if necessary.

Revision ID: 501d1179b2f0
Revises: 7e3f009cb4ae
Create Date: 2023-03-22 15:51:48.517750

"""
from alembic import op
import sqlalchemy as sa
from flask import current_app

from auth_api.models import db
from auth_api.services.keycloak import KeycloakService
from auth_api.services.products import Product
from auth_api.services.rest_service import RestService
from auth_api.utils.enums import KeycloakGroupActions

# revision identifiers, used by Alembic.
revision = '501d1179b2f0'
down_revision = '7e3f009cb4ae'
branch_labels = None
depends_on = None


def upgrade():
    # Add in products for MHR / PPR.
    conn = op.get_bind()
    org_res = conn.execute(
        "select o.id, o.bcol_user_id from orgs o where bcol_user_id is not null and bcol_account_id is not null and status_code in ('ACTIVE', 'PENDING_STAFF_REVIEW');"
    )
    orgs = org_res.fetchall()
    print('starting migration for BCOL products')
    if len(orgs) > 0:
        token = RestService.get_service_account_token()
    for org_id in orgs:
        try:
            print('Getting bcol profile for ', org_id[0], org_id[1])
            bcol_response = RestService.get(endpoint=current_app.config.get('BCOL_API_URL') + f'/profiles/{org_id[1]}',
                                            token=token)
            print('BCOL Response', bcol_response.json())
            added_subscriptions = Product.create_subscription_from_bcol_profile(org_id[0], bcol_response.json().get('profileFlags'))
            for added_subscription in added_subscriptions:
                # Check for PPR or MHR, if we have these.. add the roles in keycloak.
                added_subscription = added_subscription.lower()
                if added_subscription in ('mhr', 'ppr'):
                    user_query = conn.execute(
                        f"select keycloak_guid from users m join users u on u.id = m.user_id where m.org_id = {org_id[0]} and m.status_code = 'ACTIVE'"
                    )
                    user_keycloak_guids = user_query.fetchall()
                    for user_keycloak_guid in user_keycloak_guids:
                        print(f'Adding user {user_keycloak_guid[0]} to group: {added_subscription}')
                        try:
                            # Note - have some mechanics for this built for this next migration.
                            if added_subscription == 'mhr':
                                KeycloakService.add_or_remove_user_from_group(user_keycloak_guid, 'mhr_search_user', KeycloakGroupActions.ADD_TO_GROUP.value)
                            elif added_subscription == 'ppr':
                                KeycloakService.add_or_remove_user_from_group(user_keycloak_guid, 'ppr_user', KeycloakGroupActions.ADD_TO_GROUP.value)
                        except Exception as exc:
                            print('Error adding user to group')
                            print(exc)
        except Exception as exc:
            print('Profile Error')
            print(exc)
            raise exc
    db.session.commit()


def downgrade():
    pass

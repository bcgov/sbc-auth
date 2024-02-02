# Copyright © 2023 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests to verify the accounts API end-point.

Test-Suite to ensure that the cors flight responses are working as expected.
"""


from auth_api import status as http_status


def test_preflight_account(app, client, jwt, session):
    """Assert preflight responses for accounts are correct."""
    rv = client.options('/api/v1/accounts/1/products/1/authorizations',
                        headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_activity_log(app, client, jwt, session):
    """Assert preflight responses for activity logs are correct."""
    rv = client.options('/api/v1/orgs/1/activity-logs', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_affiliation_invitation(app, client, jwt, session):
    """Assert preflight responses for affiliation invitations are correct."""
    rv = client.options('/api/v1/affiliationInvitations', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET, POST')

    rv = client.options('/api/v1/affiliationInvitations/1', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE, GET, PATCH')

    rv = client.options('/api/v1/affiliationInvitations/1/token/ABC', headers={'Access-Control-Request-Method': 'PUT'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'PUT')

    rv = client.options('/api/v1/affiliationInvitations/1/authorization/ACTION',
                        headers={'Access-Control-Request-Method': 'PATCH'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'PATCH')


def test_preflight_bcol_profiles(app, client, jwt, session):
    """Assert preflight responses for bcol profiles are correct."""
    rv = client.options('/api/v1/bcol-profiles', headers={'Access-Control-Request-Method': 'POST'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'POST')


def test_preflight_bulk_users(app, client, jwt, session):
    """Assert preflight responses for bcol profiles are correct."""
    rv = client.options('/api/v1/bulk/users', headers={'Access-Control-Request-Method': 'POST'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'POST')


def test_preflight_codes(app, client, jwt, session):
    """Assert preflight responses for codes are correct."""
    rv = client.options('/api/v1/codes/CODETYPE', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_documents(app, client, jwt, session):
    """Assert preflight responses for documents are correct."""
    rv = client.options('/api/v1/documents/DOCTYPE', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')

    rv = client.options('/api/v1/documents/FILENAME/signatures', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')

    rv = client.options('/api/v1/documents/affidavit', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_entity(app, client, jwt, session):
    """Assert preflight responses for entity are correct."""
    rv = client.options('/api/v1/entities', headers={'Access-Control-Request-Method': 'POST'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'POST')

    rv = client.options('/api/v1/entities/BUSINESS_IDENTIFIER', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE, GET, PATCH')

    rv = client.options('/api/v1/entities/BUSINESS_IDENTIFIER/contacts',
                        headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE, GET, POST, PUT')

    rv = client.options('/api/v1/entities/BUSINESS_IDENTIFIER/authorizations',
                        headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_invitation(app, client, jwt, session):
    """Assert preflight responses for invitations are correct."""
    rv = client.options('/api/v1/invitations', headers={'Access-Control-Request-Method': 'POST'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'POST')

    rv = client.options('/api/v1/invitations/1', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE, GET, PATCH')

    rv = client.options('/api/v1/invitations/tokens/ABC', headers={'Access-Control-Request-Method': 'PUT'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET, PUT')


def test_preflight_notifications(app, client, jwt, session):
    """Assert preflight responses for notifications are correct."""
    rv = client.options('/api/v1/users/1/org/2/notifications', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_org(app, client, jwt, session):
    """Assert preflight responses for org are correct."""
    rv = client.options('/api/v1/orgs', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET, POST')

    rv = client.options('/api/v1/orgs/1', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE, GET, PATCH, PUT')

    rv = client.options('/api/v1/orgs/1/login-options', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET, POST, PUT')

    rv = client.options('/api/v1/orgs/1/contacts', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE, GET, POST, PUT')

    rv = client.options('/api/v1/orgs/1/affiliations', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET, POST')

    rv = client.options('/api/v1/orgs/affiliation/BUSINESS_IDENTIFIER',
                        headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')

    rv = client.options('/api/v1/orgs/1/affiliations/BUSINESS_IDENTIFIER',
                        headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE, GET')

    rv = client.options('/api/v1/orgs/1/members', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')

    rv = client.options('/api/v1/orgs/1/members/1', headers={'Access-Control-Request-Method': 'PATCH'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE, PATCH')

    rv = client.options('/api/v1/orgs/1/invitations', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')

    rv = client.options('/api/v1/orgs/1/admins/affidavits', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')

    rv = client.options('/api/v1/orgs/1/payment_info', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_org_api_keys(app, client, jwt, session):
    """Assert preflight responses for org api keys are correct."""
    rv = client.options('/api/v1/orgs/1/api-keys', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET, POST')

    rv = client.options('/api/v1/orgs/1/api-keys/KEY', headers={'Access-Control-Request-Method': 'DELETE'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE')


def test_preflight_org_authorizations(app, client, jwt, session):
    """Assert preflight responses for org authorizations are correct."""
    rv = client.options('/api/v1/orgs/1/authorizations', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_org_products(app, client, jwt, session):
    """Assert preflight responses for org products are correct."""
    rv = client.options('/api/v1/orgs/1/products', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET, POST')


def test_preflight_org_permissions(app, client, jwt, session):
    """Assert preflight responses for org permissions are correct."""
    rv = client.options('/api/v1/permissions/ORG_STATUS/MEMBERSHIP_TYPE',
                        headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_products(app, client, jwt, session):
    """Assert preflight responses for products are correct."""
    rv = client.options('/api/v1/products', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_task(app, client, jwt, session):
    """Assert preflight responses for tasks are correct."""
    rv = client.options('/api/v1/tasks', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')

    rv = client.options('/api/v1/tasks/1', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET, PUT')


def test_preflight_user(app, client, jwt, session):
    """Assert preflight responses for user are correct."""
    rv = client.options('/api/v1/users', headers={'Access-Control-Request-Method': 'POST'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET, POST')

    rv = client.options('/api/v1/users/bcros', headers={'Access-Control-Request-Method': 'POST'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'POST')

    rv = client.options('/api/v1/users/USERNAME/otp', headers={'Access-Control-Request-Method': 'DELETE'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE')

    rv = client.options('/api/v1/users/USERNAME', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE, GET, PATCH')

    rv = client.options('/api/v1/users/@me', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE, GET, PATCH')

    rv = client.options('/api/v1/users/contacts', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'DELETE, GET, POST, PUT')

    rv = client.options('/api/v1/users/orgs', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')

    rv = client.options('/api/v1/users/orgs/123/membership', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')

    rv = client.options('/api/v1/users/USERGUID/affidavits', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET, POST')

    rv = client.options('/api/v1/users/authorizations', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_simple_org(app, client, jwt, session):
    """Assert preflight responses for simple org are correct."""
    rv = client.options('/api/v1/orgs/simple', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def test_preflight_user_settings(app, client, jwt, session):
    """Assert preflight responses for user settings are correct."""
    rv = client.options('/api/v1/users/1/settings', headers={'Access-Control-Request-Method': 'GET'})
    assert rv.status_code == http_status.HTTP_200_OK
    assert_access_control_headers(rv, '*', 'GET')


def assert_access_control_headers(rv, origins: str, methods: str):
    """Assert access control headers are correct."""
    assert rv.headers['Access-Control-Allow-Origin'] == origins
    assert rv.headers['Access-Control-Allow-Methods'] == methods

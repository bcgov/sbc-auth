# Copyright © 2019 Province of British Columbia
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

"""Tests to assure the permissions API end-point.

Test-Suite to ensure that the /permissions endpoint is working as expected.
"""

import json
from http import HTTPStatus

from tests.utilities.factory_scenarios import TestJwtClaims
from tests.utilities.factory_utils import factory_auth_header


def test_permissions_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert get permissions endpoint returns 200."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get("/api/v1/permissions/active/admin?case=upper", headers=headers, content_type="application/json")

    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    present = "CHANGE_ORG_NAME" in dictionary
    assert present is True

    """Assert get permissions endpoint returns 200."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get("/api/v1/permissions/foo/bar", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    assert len(dictionary) == 0


def test_returns_empty_string_permissions(client, jwt, session):  # pylint:disable=unused-argument
    """Assert get permissions endpoint returns 200."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get("/api/v1/permissions/active/admin?case=upper", headers=headers, content_type="application/json")

    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    present = "VIEW_USER_LOGINSOURCE" in dictionary
    assert present is True

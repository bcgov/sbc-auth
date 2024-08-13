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

"""Tests to verify the reset API end-point.

Test-Suite to ensure that the /tester/reset endpoint is working as expected.
"""
import json
from http import HTTPStatus
from unittest.mock import patch

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.services import ResetTestData as ResetDataService
from tests.utilities.factory_scenarios import TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_auth_header


def test_reset(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert the endpoint can reset the test data."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.tester_role)
    rv = client.post("/test/reset", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.NO_CONTENT


def test_reset_unauthorized(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert the endpoint get a unauthorized error if don't have tester role."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/test/reset", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_reset_returns_exception(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the code type can not be fetched and with expcetion."""
    with patch.object(ResetDataService, "reset", side_effect=BusinessException(Error.UNDEFINED_ERROR, None)):
        headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.tester_role)
        rv = client.post("/test/reset", headers=headers, content_type="application/json")
        assert rv.status_code == HTTPStatus.BAD_REQUEST

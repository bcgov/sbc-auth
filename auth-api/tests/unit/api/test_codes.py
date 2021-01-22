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

"""Tests to verify the entities API end-point.

Test-Suite to ensure that the /entities endpoint is working as expected.
"""

from unittest.mock import patch

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.schemas import utils as schema_utils
from auth_api.services import Codes as CodesService


def test_get_codes(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the code type can be fetched."""
    code_type = 'membership_types'
    rv = client.get('/api/v1/codes/{}'.format(code_type), content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'codes')[0]

    rv = client.get('/api/v1/codes/{}'.format(code_type.upper()), content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(rv.json, 'codes')[0]


def test_get_codes_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the code type can not be fetched."""
    rv = client.get('/api/v1/codes/{}'.format('aaaaaaa'), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND

    rv = client.get('/api/v1/codes/{}'.format(''), content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_get_codes_returns_exception(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that the code type can not be fetched and with expcetion."""
    with patch.object(CodesService, 'fetch_codes', side_effect=BusinessException(Error.UNDEFINED_ERROR, None)):
        rv = client.get('/api/v1/codes/{}'.format('membership_type'), content_type='application/json')
        assert rv.status_code == http_status.HTTP_400_BAD_REQUEST

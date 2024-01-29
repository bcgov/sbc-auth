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
"""Tests to verify the User Service.

Test-Suite to ensure that the User Service is working as expected.
"""
import importlib
from unittest.mock import patch

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.services import Codes as CodesService


def test_fetch_data_model(session):  # pylint: disable=unused-argument
    """Assert that code type details can be fetch by table name."""
    code_type = 'membership_types'
    code_result = CodesService.fetch_data_model(code_type)
    assert code_result is not None


def test_fetch_data_model_not_found(session):  # pylint: disable=unused-argument
    """Assert that code type details can be fetch by table name."""
    code_type = 'membership_type1'
    code_result = CodesService.fetch_data_model(code_type)
    assert not code_result

    code_type = 'user'
    code_result = CodesService.fetch_data_model(code_type)
    assert not code_result

    code_type = ''
    code_result = CodesService.fetch_data_model(code_type)
    assert not code_result


def test_fetch_codes(session):  # pylint: disable=unused-argument
    """Assert that code type details can be fetch by table name."""
    code_type = 'membership_types'
    data = CodesService.fetch_codes(code_type)
    assert data is not None
    assert data[0]['name'] == 'USER'


def test_fetch_codes_not_found(session):  # pylint: disable=unused-argument
    """Assert that code type details can not be fetch by table name."""
    # Table is not exists
    code_type = 'membership_type1'
    data = CodesService.fetch_codes(code_type)
    assert not data

    data = CodesService.fetch_codes(None)
    assert not data

    data = CodesService.fetch_codes('')
    assert not data

    # The table is not the code, type or status table.
    code_type = 'user'
    data = CodesService.fetch_codes(code_type)
    assert not data


def test_fetch_codes_with_exception(session):  # pylint: disable=unused-argument
    """Assert that code type details can not be fetch by table name."""
    code_type = 'membership_types'
    with patch.object(importlib, 'import_module', side_effect=Exception(Error.UNDEFINED_ERROR, None)):
        with pytest.raises(BusinessException) as exception:
            CodesService.fetch_codes(code_type)

        assert exception.value.code == 'UNDEFINED_ERROR'

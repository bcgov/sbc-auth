"""Tests for the pay utility functions."""

# Copyright © 2026 Province of British Columbia
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

from unittest.mock import Mock

from flask import current_app

from auth_api.utils.enums import AccessType, ProductCode
from auth_api.utils.pay import get_account_fees
from tests.conftest import mock_token
from tests.utilities.factory_utils import factory_org_model


def test_get_account_fees_govm_org_success(monkeypatch, session):  # pylint:disable=unused-argument
    """Test that GOVM org with successful response returns list of product codes."""
    org = factory_org_model(org_info={"name": "Org 1", "accessType": AccessType.GOVM.value})

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "accountFees": [
            {"product": ProductCode.BUSINESS.value},
            {"product": ProductCode.VS.value},
            {"product": ProductCode.BCA.value},
        ]
    }

    current_app.config["PAY_API_URL"] = "http://pay-api.test"

    monkeypatch.setattr("auth_api.utils.pay.RestService.get_service_account_token", mock_token)
    monkeypatch.setattr("auth_api.utils.pay.RestService.get", lambda *args, **kwargs: mock_response)  # noqa: ARG005

    result = get_account_fees(org)

    assert result == [
        ProductCode.BUSINESS.value,
        ProductCode.VS.value,
        ProductCode.BCA.value,
    ]

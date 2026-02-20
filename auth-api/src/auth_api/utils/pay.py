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
"""Pay API utility functions."""

from flask import current_app

from auth_api.exceptions.errors import Error
from auth_api.models import Org as OrgModel
from auth_api.services.rest_service import RestService
from auth_api.utils.roles import GOV_ORG_TYPES


def get_account_fees(org: OrgModel) -> list[str]:
    """Fetch all account fees from pay-api and return a dict mapping product codes to fee existence."""
    if org.access_type not in GOV_ORG_TYPES:
        return []
    pay_url = current_app.config.get("PAY_API_URL")
    account_fees = []

    try:
        token = RestService.get_service_account_token()
        response = RestService.get(endpoint=f"{pay_url}/accounts/{org.id}/fees", token=token, retry_on_failure=True)

        if response and response.status_code == 200:
            response_data = response.json()
            account_fees_obj = response_data.get("accountFees", [])

            for fee in account_fees_obj:
                product_code = fee.get("product")
                if product_code:
                    account_fees.append(product_code)
            return account_fees
    except Exception as e:  # NOQA # pylint: disable=broad-except
        # Log the error but don't fail the subscription creation
        # Return empty dict so subscription can proceed without fee-based review logic
        current_app.logger.info(f"{Error.ACCOUNT_FEES_FETCH_FAILED} for org {org.id}: {e}")
        return []

    return account_fees

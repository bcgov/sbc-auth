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
"""Client for the COLIN API.

Used to source entity details for businesses that are managed in COLIN and are not
loaded in LEAR, so they can be affiliated from the business registry dashboard.
"""

import re
from http import HTTPStatus

from flask import current_app
from requests.exceptions import HTTPError

from auth_api.services.rest_service import RestService


class Colin:
    """Fetch business details from the COLIN API."""

    # FUTURE: This pattern will need to be updated in the future if we want to reuse the same flow for expros etc.
    COLIN_IDENTIFIER_PATTERN = re.compile(r"^BC\d{7}$")

    @staticmethod
    def is_colin_identifier(business_identifier: str) -> bool:
        """Return True if the identifier could belong to a COLIN business not loaded in LEAR."""
        return bool(business_identifier and Colin.COLIN_IDENTIFIER_PATTERN.match(business_identifier))

    @staticmethod
    def is_affiliation_eligible_type(corp_type: str) -> bool:
        """Return True for corp types that are eligible for affiliation from COLIN.
        
        Configured in COLIN_AFFILIATION_CORP_TYPES.
        """
        if not corp_type:
            return False
        return corp_type.upper() in current_app.config.get("COLIN_AFFILIATION_CORP_TYPES", [])

    @staticmethod
    def fetch_auth_info(business_identifier: str) -> dict | None:
        """Return the COLIN info auth is interested in for a business, or None when not found.

        Contains the business passcode. Never log the returned dict, and never
        pass it back to a caller outside of entity creation/sync.
        """
        colin_api_url = current_app.config.get("COLIN_API_URL")
        if not colin_api_url:
            current_app.logger.error("COLIN_API_URL is not configured; cannot sync COLIN entity")
            return None

        endpoint = f"{colin_api_url}/businesses/{business_identifier}/auth-info"
        token = RestService.get_service_account_token(
            config_id="ENTITY_SVC_CLIENT_ID",
            config_secret="ENTITY_SVC_CLIENT_SECRET",  # noqa: S106
        )

        try:
            response = RestService.get(
                endpoint=endpoint,
                token=token,
                skip_404_logging=True,
                # response carries the passcode - keep it out of the logs
                skip_response_logging=True,
            )
        except HTTPError as exc:
            if exc.response is not None and exc.response.status_code == HTTPStatus.NOT_FOUND:
                current_app.logger.debug(f"COLIN auth info not found for {business_identifier}")
                return None
            raise

        return response.json()

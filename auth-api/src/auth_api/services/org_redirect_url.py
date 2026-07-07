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
"""Service for managing org redirect URLs."""

from __future__ import annotations

from urllib.parse import urlparse

from auth_api.models.org_redirect_url import OrgRedirectUrl as OrgRedirectUrlModel


class OrgRedirectUrl:
    """Service for managing org redirect URLs."""

    @staticmethod
    def get_all(org_id: int) -> list[OrgRedirectUrlModel]:
        """Return all redirect URLs for the org."""
        return OrgRedirectUrlModel.find_by_org_id(org_id)

    @staticmethod
    def create(org_id: int, url: str) -> tuple[OrgRedirectUrlModel | None, str | None]:
        """Create a new redirect URL for the org.

        Returns (record, None) on success, or (None, error_message) on failure.
        """
        url = url.strip()
        error = OrgRedirectUrl._validate(url)
        if error:
            return None, error

        if OrgRedirectUrlModel.find_active_by_org_and_url(org_id, url):
            return None, "This URL has already been added."

        record = OrgRedirectUrlModel(org_id=org_id, redirect_url=url)
        record.save()
        return record, None

    @staticmethod
    def update(url_id: int, org_id: int, url: str) -> tuple[OrgRedirectUrlModel | None, str | None]:
        """Update an existing redirect URL.

        Returns (record, None) on success, or (None, error_message) on failure.
        """
        record = OrgRedirectUrlModel.find_by_id_and_org(url_id, org_id)
        if not record:
            return None, "not_found"

        url = url.strip()
        error = OrgRedirectUrl._validate(url)
        if error:
            return None, error

        existing = OrgRedirectUrlModel.find_active_by_org_and_url(org_id, url)
        if existing and existing.id != url_id:
            return None, "This URL has already been added."

        record.redirect_url = url
        record.save()
        return record, None

    @staticmethod
    def delete(url_id: int, org_id: int) -> bool:
        """Delete a redirect URL by ID scoped to the org. Returns False if not found."""
        record = OrgRedirectUrlModel.find_by_id_and_org(url_id, org_id)
        if not record:
            return False
        record.delete()
        return True

    @staticmethod
    def is_valid_redirect_url(org_id: int, url: str) -> bool:
        """Return True if the URL is registered for the org."""
        return OrgRedirectUrlModel.is_valid_redirect_url(org_id, url)

    @staticmethod
    def _validate(url: str) -> str | None:
        """Return an error message if the URL is invalid, else None."""
        if not url:
            return "Enter a redirect URL."
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return "Enter a valid URL beginning with http:// or https://."
        return None

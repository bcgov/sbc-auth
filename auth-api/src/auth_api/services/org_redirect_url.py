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

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.org_redirect_url import OrgRedirectUrl as OrgRedirectUrlModel


class OrgRedirectUrl:
    """Service for managing org redirect URLs."""

    @staticmethod
    def get_all(org_id: int) -> list[OrgRedirectUrlModel]:
        """Return all redirect URLs for the org."""
        return OrgRedirectUrlModel.find_by_org_id(org_id)

    @staticmethod
    def create(org_id: int, url: str) -> OrgRedirectUrlModel:
        """Create a new redirect URL for the org. Raises BusinessException on validation failure."""
        url = OrgRedirectUrl._validate(url)

        if OrgRedirectUrlModel.find_by_org_and_url(org_id, url):
            raise BusinessException(Error.REDIRECT_URL_ALREADY_EXISTS, None)

        record = OrgRedirectUrlModel(org_id=org_id, redirect_url=url)
        record.save()
        return record

    @staticmethod
    def update(url_id: int, org_id: int, url: str) -> OrgRedirectUrlModel | None:
        """Update an existing redirect URL. Raises BusinessException on validation failure."""
        record = OrgRedirectUrlModel.find_by_id_and_org(url_id, org_id)
        if not record:
            return None

        url = OrgRedirectUrl._validate(url)

        existing = OrgRedirectUrlModel.find_by_org_and_url(org_id, url)
        if existing and existing.id != url_id:
            raise BusinessException(Error.REDIRECT_URL_ALREADY_EXISTS, None)

        record.redirect_url = url
        record.save()
        return record

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
    def _validate(url: str) -> str:
        """Return the trimmed URL, or raise BusinessException if invalid.

        A trailing ``/*`` is allowed to mark the URL as a path-prefix wildcard match.
        A ``*`` anywhere else in the URL is rejected.
        """
        url = url.strip()
        if not url:
            raise BusinessException(Error.REDIRECT_URL_REQUIRED, None)
        if "*" in url and not url.endswith("/*"):
            raise BusinessException(Error.INVALID_REDIRECT_URL, None)
        base_url = url[:-1] if url.endswith("/*") else url
        parsed = urlparse(base_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise BusinessException(Error.INVALID_REDIRECT_URL, None)
        return url

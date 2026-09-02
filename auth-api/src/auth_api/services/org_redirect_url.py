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

import re
from urllib.parse import urlsplit, urlunsplit

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.org_redirect_url import OrgRedirectUrl as OrgRedirectUrlModel

# For sanitizing accepted redirect urls
SAFE_HOST_CHARS = re.compile(r"[A-Za-z0-9.-]+(:[0-9]+)?")
SAFE_PATH_CHARS = re.compile(r"[A-Za-z0-9\-._~/*]*")


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
        """Return True if the given URL matches a redirect URL registered for the org.

        The incoming URL's query string and fragment are ignored, so a registered
        ``/callback`` accepts ``/callback?ref=abc``. A registered URL ending in ``/*`` also
        matches any URL sharing that path prefix. The trailing slash acts as a boundary,
        so ``/callback/*`` never matches ``/callback-other``.
        """
        if not url or not OrgRedirectUrl._has_safe_characters(url):
            return False
        parsed = urlsplit(url)
        incoming = urlunsplit(parsed._replace(netloc=parsed.netloc.lower(), query="", fragment=""))
        for record in OrgRedirectUrlModel.find_by_org_id(org_id):
            pattern = record.redirect_url
            if pattern.endswith("/*"):
                if incoming.startswith(pattern[:-1]):
                    return True
            elif incoming == pattern:
                return True
        return False

    @staticmethod
    def _has_safe_characters(url: str) -> bool:
        """Return True if the URL's host and path are free of characters we do not accept.

        The raw string is checked for control characters and non-ASCII before parsing, because
        urlsplit strips tab and newline. Host and path are then checked against their allowed
        character sets, and a ``..`` is rejected.
        """
        if not url.isascii() or not url.isprintable():
            return False
        parsed = urlsplit(url)
        if not SAFE_HOST_CHARS.fullmatch(parsed.netloc) or not SAFE_PATH_CHARS.fullmatch(parsed.path):
            return False
        return ".." not in parsed.path.split("/")

    @staticmethod
    def _validate(url: str) -> str:
        """Return the trimmed URL, or raise BusinessException if invalid.

        A trailing ``/*`` is allowed to mark the URL as a path-prefix wildcard match.
        A ``*`` anywhere else in the URL is rejected.
        A query string or fragment is rejected — query params can be dynamic, we will validate
        on the path itself.
        """
        url = url.strip()
        if not url:
            raise BusinessException(Error.REDIRECT_URL_REQUIRED, None)
        if not OrgRedirectUrl._has_safe_characters(url):
            raise BusinessException(Error.INVALID_REDIRECT_URL, None)
        is_wildcard = url.endswith("/*")
        if "*" in url and not is_wildcard:
            raise BusinessException(Error.INVALID_REDIRECT_URL, None)
        base_url = url[:-1] if is_wildcard else url
        parsed = urlsplit(base_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise BusinessException(Error.INVALID_REDIRECT_URL, None)
        if parsed.query or parsed.fragment:
            raise BusinessException(Error.INVALID_REDIRECT_URL, None)
        normalized = urlunsplit(parsed._replace(netloc=parsed.netloc.lower()))
        return f"{normalized}*" if is_wildcard else normalized

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
"""This manages an OrgRedirectUrl record in the Auth service.

A redirect URL is a pre-registered endpoint belonging to a vendor (API) org.
After a law firm completes the linking flow, BCROS redirects back to one of
these URLs with the linking key appended as a query parameter.
"""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String

from .base_model import BaseModel


class OrgRedirectUrl(BaseModel):
    """This is the model for an OrgRedirectUrl."""

    __tablename__ = "org_redirect_urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(
        ForeignKey("orgs.id"), nullable=False, index=True,
        comment="Vendor org that owns this redirect URL",
    )
    redirect_url = Column(
        String(2048), nullable=False,
        comment="Full URL to which BCROS may redirect after linking; must be https",
    )

    @classmethod
    def find_by_org_id(cls, org_id: int) -> list[OrgRedirectUrl]:
        """Return all redirect URLs for the given org, newest first."""
        return cls.query.filter_by(org_id=org_id).order_by(cls.id.desc()).all()

    @classmethod
    def find_by_id_and_org(cls, url_id: int, org_id: int) -> OrgRedirectUrl | None:
        """Return a redirect URL by ID, scoped to the org for ownership check."""
        return cls.query.filter_by(id=url_id, org_id=org_id).one_or_none()

    @classmethod
    def find_active_by_org_and_url(cls, org_id: int, url: str) -> OrgRedirectUrl | None:
        """Return an existing redirect URL record matching the given url for the org."""
        return cls.query.filter_by(org_id=org_id, redirect_url=url).one_or_none()

    @classmethod
    def is_valid_redirect_url(cls, org_id: int, url: str) -> bool:
        """Return True if the given URL is registered for the org."""
        return cls.find_active_by_org_and_url(org_id, url) is not None

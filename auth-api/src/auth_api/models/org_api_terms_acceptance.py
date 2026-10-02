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
"""This manages an OrgApiTermsAcceptance record in the Auth service.

One row is recorded per org per API Terms of Use document version accepted.
The inherited created / created_by_id columns hold when and by whom the terms were accepted.
"""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint

from .base_model import BaseModel


class OrgApiTermsAcceptance(BaseModel):
    """This is the model for an OrgApiTermsAcceptance."""

    __tablename__ = "org_api_terms_acceptances"
    __table_args__ = (UniqueConstraint("org_id", "version_id", name="uq_org_api_terms_org_version"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(
        ForeignKey("orgs.id"),
        nullable=False,
        index=True,
        comment="Org that accepted the API Terms of Use",
    )
    version_id = Column(
        ForeignKey("documents.version_id"),
        nullable=False,
        comment="Version of the termsofuse_api document that was accepted",
    )

    @classmethod
    def find_by_org_and_version(cls, org_id: int, version_id: str) -> OrgApiTermsAcceptance | None:
        """Return the org's acceptance of the given terms version, if any."""
        return cls.query.filter_by(org_id=org_id, version_id=version_id).one_or_none()

    @classmethod
    def find_latest_by_org(cls, org_id: int) -> OrgApiTermsAcceptance | None:
        """Return the org's most recent acceptance, if any."""
        return cls.query.filter_by(org_id=org_id).order_by(cls.created.desc(), cls.id.desc()).first()

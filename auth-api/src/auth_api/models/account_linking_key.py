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
"""This manages an AccountLinkingKey record in the Auth service.

A linking key allows a vendor account (e.g. ALF) to access the affiliated
businesses of a source account (e.g. a lawfirm) via a shared secret key.
The vendor pays for transactions; the source account's businesses are accessed.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from auth_api.utils.enums import LinkingKeyStatus

from .base_model import BaseModel


class AccountLinkingKey(BaseModel):
    """This is the model for an AccountLinkingKey."""

    __tablename__ = "account_linking_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    linking_key = Column(String(100), nullable=False, unique=True, index=True)
    # Source account whose businesses are shared (e.g. lawfirm)
    account_id = Column(ForeignKey("orgs.id"), nullable=False, index=True)
    # Vendor account that uses the key (e.g. ALF); bound at generation or locked on first use
    vendor_account_id = Column(ForeignKey("orgs.id"), nullable=True, index=True)
    status = Column(String(20), nullable=False, default=LinkingKeyStatus.ACTIVE.value)
    expires_on = Column(DateTime(timezone=True), nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    account = relationship("Org", foreign_keys=[account_id], lazy="select")
    vendor_account = relationship("Org", foreign_keys=[vendor_account_id], lazy="select")

    @classmethod
    def find_active_by_key(cls, key: str) -> AccountLinkingKey | None:
        """Return an active, non-expired linking key record."""
        return (
            cls.query.filter_by(linking_key=key, status=LinkingKeyStatus.ACTIVE.value)
            .filter(cls.expires_on > datetime.now(UTC))
            .one_or_none()
        )

    @classmethod
    def find_active_by_account_id(cls, account_id: int) -> list[AccountLinkingKey]:
        """Return all active linking keys for the given source account."""
        return cls.query.filter_by(account_id=account_id, status=LinkingKeyStatus.ACTIVE.value).all()

    @classmethod
    def find_active_by_id(cls, key_id: int, account_id: int) -> AccountLinkingKey | None:
        """Return an active key by ID, scoped to the account for ownership check."""
        return cls.query.filter_by(id=key_id, account_id=account_id, status=LinkingKeyStatus.ACTIVE.value).one_or_none()

    @classmethod
    def find_active_by_account_and_vendor(cls, account_id: int, vendor_account_id: int) -> AccountLinkingKey | None:
        """Return the single active key for an (account, vendor) pair."""
        return cls.query.filter_by(
            account_id=account_id, vendor_account_id=vendor_account_id, status=LinkingKeyStatus.ACTIVE.value
        ).one_or_none()


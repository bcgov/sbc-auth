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
from sqlalchemy.orm import joinedload, relationship

from auth_api.utils.enums import LinkingKeyStatus

from .base_model import BaseModel


class AccountLinkingKey(BaseModel):
    """This is the model for an AccountLinkingKey."""

    __tablename__ = "account_linking_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    linking_key = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Cryptographically random URL-safe secret shared with the vendor",
    )
    account_id = Column(
        ForeignKey("orgs.id"),
        nullable=False,
        index=True,
        comment="Source account (e.g. lawfirm) whose affiliated businesses are accessible via this key",
    )
    vendor_account_id = Column(
        ForeignKey("orgs.id"),
        nullable=True,
        index=True,
        comment="Vendor account (e.g. ALF) that is authorized to use this key; set at generation time",
    )
    status = Column(
        String(20),
        nullable=False,
        default=LinkingKeyStatus.ACTIVE.value,
        comment="ACTIVE (bound and usable), PENDING (unbound, awaiting vendor), or REVOKED",
    )
    expires_on = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="UTC timestamp after which the key is no longer valid",
    )
    last_used = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="UTC timestamp of the most recent successful validation",
    )
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
    def find_by_account_id(cls, account_id: int) -> list[AccountLinkingKey]:
        """Return all non-revoked (ACTIVE and PENDING) linking keys for the given source account."""
        return (
            cls.query.filter(
                cls.account_id == account_id,
                cls.status.in_([LinkingKeyStatus.ACTIVE.value, LinkingKeyStatus.PENDING.value]),
            )
            .options(joinedload(cls.vendor_account), joinedload(cls.created_by))
            .all()
        )

    @classmethod
    def find_by_id(cls, key_id: int, account_id: int) -> AccountLinkingKey | None:
        """Return a non-revoked (ACTIVE or PENDING) key by ID, scoped to the account."""
        return cls.query.filter(
            cls.id == key_id,
            cls.account_id == account_id,
            cls.status.in_([LinkingKeyStatus.ACTIVE.value, LinkingKeyStatus.PENDING.value]),
        ).one_or_none()

    @classmethod
    def find_active_by_account_and_vendor(cls, account_id: int, vendor_account_id: int) -> AccountLinkingKey | None:
        """Return the single active key for an (account, vendor) pair."""
        return cls.query.filter_by(
            account_id=account_id, vendor_account_id=vendor_account_id, status=LinkingKeyStatus.ACTIVE.value
        ).one_or_none()

    @classmethod
    def find_pending_by_account(cls, account_id: int) -> AccountLinkingKey | None:
        """Return the single unbound (PENDING) key for an account, if any."""
        return cls.query.filter_by(account_id=account_id, status=LinkingKeyStatus.PENDING.value).one_or_none()

    @classmethod
    def find_pending_by_key(cls, key: str) -> AccountLinkingKey | None:
        """Return a non-expired PENDING key matching the given value."""
        return cls.query.filter(
            cls.linking_key == key,
            cls.status == LinkingKeyStatus.PENDING.value,
            cls.expires_on > datetime.now(UTC),
        ).one_or_none()

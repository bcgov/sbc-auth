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
"""Service for managing account linking keys."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from flask import current_app

from auth_api.models.account_linking_key import AccountLinkingKey as AccountLinkingKeyModel
from auth_api.models.dataclass import Activity
from auth_api.models.db import db
from auth_api.services.activity_log_publisher import ActivityLogPublisher
from auth_api.utils.enums import ActivityAction, LinkingKeyStatus


class AccountLinkingKey:
    """Service for managing account linking keys."""

    @staticmethod
    def generate(account_id: int, vendor_account_id: int) -> AccountLinkingKeyModel:
        """Generate a new linking key bound to the given vendor.

        Each (account, vendor) pair can have at most one active key — any existing one is revoked.
        """
        existing = AccountLinkingKeyModel.find_active_by_account_and_vendor(account_id, vendor_account_id)
        if existing:
            existing.status = LinkingKeyStatus.REVOKED.value
            db.session.flush()

        record = AccountLinkingKeyModel(
            linking_key=secrets.token_urlsafe(32),
            account_id=account_id,
            vendor_account_id=vendor_account_id,
            status=LinkingKeyStatus.ACTIVE.value,
            expires_on=datetime.now(UTC) + timedelta(days=current_app.config.get("LINKING_KEY_EXPIRY_DAYS", 365)),
        )
        record.save()

        ActivityLogPublisher.publish_activity(
            Activity(
                org_id=account_id,
                action=ActivityAction.LINKING_KEY_GENERATED.value,
                name=str(account_id),
                id=str(record.id),
                value=str(vendor_account_id),
            )
        )
        return record

    @staticmethod
    def get_all(account_id: int) -> list[AccountLinkingKeyModel]:
        """Return all active linking keys for the account."""
        return AccountLinkingKeyModel.find_active_by_account_id(account_id)

    @staticmethod
    def revoke(key_id: int, account_id: int) -> bool:
        """Soft-delete (revoke) a linking key by ID, scoped to the account. Returns False if not found."""
        record = AccountLinkingKeyModel.find_active_by_id(key_id, account_id)
        if not record:
            return False
        record.status = LinkingKeyStatus.REVOKED.value
        record.save()
        ActivityLogPublisher.publish_activity(
            Activity(
                org_id=account_id,
                action=ActivityAction.LINKING_KEY_REVOKED.value,
                name=str(account_id),
                id=str(record.id),
                value=str(record.vendor_account_id) if record.vendor_account_id else None,
            )
        )
        return True

    @staticmethod
    def validate(key: str, vendor_account_id: int) -> AccountLinkingKeyModel | None:
        """Validate a linking key for the given vendor and return the record if authorized.

        Returns None if the key is not found, expired, revoked, or the vendor does not match.
        Updates last_used on every successful call.
        """
        record = AccountLinkingKeyModel.find_active_by_key(key)
        if not record:
            return None

        if record.vendor_account_id != int(vendor_account_id):
            current_app.logger.debug("Linking key rejected: vendor account does not match.")
            return None

        record.last_used = datetime.now(UTC)
        record.save()
        return record

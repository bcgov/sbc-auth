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
"""Task to notify accounts of expiring and expired account linking keys."""

from datetime import UTC, datetime, timedelta

from flask import current_app
from sbc_common_components.utils.enums import QueueMessageTypes
from sqlalchemy.orm import joinedload

from auth_api.models.account_linking_key import AccountLinkingKey as AccountLinkingKeyModel
from auth_api.models.dataclass import Activity
from auth_api.services.activity_log_publisher import ActivityLogPublisher
from auth_api.utils.account_mailer import publish_to_mailer
from auth_api.utils.date import utc_to_pacific_isoformat
from auth_api.utils.enums import ActivityAction, LinkingKeyStatus, QueueSources


class AccountLinkNotificationsTask:  # pylint: disable=too-few-public-methods
    """Task to notify accounts of expiring and expired account linking keys."""

    @classmethod
    def notify(cls):
        """Find expiring and expired linking keys, update status, and publish mailer notifications."""
        now = datetime.now(UTC)

        expiring_keys = cls._find_expiring_soon(now)
        current_app.logger.info(f"account_link_notifications: {len(expiring_keys)} key(s) expiring soon")
        for key in expiring_keys:
            cls._notify(key, is_reminder=True)

        expired_keys = cls._find_expired(now)
        current_app.logger.info(f"account_link_notifications: {len(expired_keys)} key(s) expired")
        for key in expired_keys:
            key.status = LinkingKeyStatus.EXPIRED.value
            key.save()
            cls._publish_expired_activity(key)
            cls._notify(key, is_reminder=False)

    @staticmethod
    def _find_expired(now: datetime) -> list[AccountLinkingKeyModel]:
        """Return ACTIVE keys whose expiry has already passed."""
        return (
            AccountLinkingKeyModel.query.options(joinedload(AccountLinkingKeyModel.vendor_account))
            .filter(
                AccountLinkingKeyModel.status == LinkingKeyStatus.ACTIVE.value,
                AccountLinkingKeyModel.expires_on <= now,
            )
            .all()
        )

    @staticmethod
    def _find_expiring_soon(now: datetime) -> list[AccountLinkingKeyModel]:
        """Return ACTIVE keys expiring exactly ACCOUNT_LINK_EXPIRY_REMINDER_DAYS from now (day-bucketed)."""
        reminder_days = current_app.config.get("ACCOUNT_LINK_EXPIRY_REMINDER_DAYS", 30)
        target = now + timedelta(days=reminder_days)
        window_start = target.replace(hour=0, minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(days=1)
        return (
            AccountLinkingKeyModel.query.options(joinedload(AccountLinkingKeyModel.vendor_account))
            .filter(
                AccountLinkingKeyModel.status == LinkingKeyStatus.ACTIVE.value,
                AccountLinkingKeyModel.expires_on >= window_start,
                AccountLinkingKeyModel.expires_on < window_end,
            )
            .all()
        )

    @staticmethod
    def _publish_expired_activity(key: AccountLinkingKeyModel) -> None:
        """Publish an activity log event for a key that has just been marked EXPIRED."""
        ActivityLogPublisher.publish_activity(
            Activity(
                org_id=key.account_id,
                action=ActivityAction.LINKING_KEY_EXPIRED.value,
                name=str(key.account_id),
                id=str(key.id),
                value=f"{key.vendor_account.name} ({key.vendor_account_id})",
            )
        )

    @staticmethod
    def _notify(key: AccountLinkingKeyModel, is_reminder: bool) -> None:
        """Publish an account-link expiry email notification to the account mailer."""
        data = {
            "accountId": key.account_id,
            "serviceProviderName": key.vendor_account.name,
            "linkDate": utc_to_pacific_isoformat(key.created),
            "expiryDate": utc_to_pacific_isoformat(key.expires_on),
            "isReminder": is_reminder,
        }
        try:
            publish_to_mailer(
                QueueMessageTypes.ACCOUNT_LINK_EXPIRY.value, data=data, source=QueueSources.AUTH_JOBS.value
            )
        except Exception as e:  # noqa: B901
            current_app.logger.warning(f"AccountLinkNotificationsTask._notify failed for key {key.id}: {e}")

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

"""Tests to assure the AccountLinkNotificationsTask.

Test-Suite to ensure that expiring and expired account linking keys are notified correctly.
"""

import secrets
from datetime import UTC, datetime
from unittest.mock import patch

from freezegun import freeze_time

from auth_api.models.account_linking_key import AccountLinkingKey as AccountLinkingKeyModel
from auth_api.models.org import Org as OrgModel
from auth_api.models.org_status import OrgStatus as OrgStatusModel
from auth_api.models.org_type import OrgType as OrgTypeModel
from auth_api.utils.enums import LinkingKeyStatus
from tasks.account_link_notifications import AccountLinkNotificationsTask

CREATED_ON = datetime(2026, 1, 15, 18, 0, 0, tzinfo=UTC)
CREATED_ON_PACIFIC_ISO = "2026-01-15"

NOW = datetime(2026, 7, 15, 18, 0, 0, tzinfo=UTC)

EXPIRES_ON_30_DAYS = datetime(2026, 8, 14, 18, 0, 0, tzinfo=UTC)
EXPIRES_ON_30_DAYS_PACIFIC_ISO = "2026-08-14"

EXPIRES_ON_PAST = datetime(2026, 7, 14, 18, 0, 0, tzinfo=UTC)
EXPIRES_ON_PAST_PACIFIC_ISO = "2026-07-14"

EXPIRES_IN_FUTURE = datetime(2027, 1, 31, 18, 0, 0, tzinfo=UTC)


def _factory_org(name: str) -> OrgModel:
    org = OrgModel(name=name)
    org.org_type = OrgTypeModel.get_default_type()
    org.org_status = OrgStatusModel.get_default_status()
    org.save()
    return org


def _factory_linking_key(
    account_id: int, vendor_account_id: int, status: str, expires_on: datetime, created_on: datetime
) -> AccountLinkingKeyModel:
    record = AccountLinkingKeyModel(
        linking_key=secrets.token_urlsafe(32),
        account_id=account_id,
        vendor_account_id=vendor_account_id,
        status=status,
        expires_on=expires_on,
    )
    record.save()
    record.created = created_on
    record.save()
    return record


def test_expiring_soon_key_sends_reminder(session, app):
    """Assert that a key expiring in exactly the reminder window sends a reminder without changing status."""
    source_org = _factory_org("Source Org")
    vendor_org = _factory_org("Vendor Org")
    key = _factory_linking_key(
        source_org.id, vendor_org.id, LinkingKeyStatus.ACTIVE.value, EXPIRES_ON_30_DAYS, CREATED_ON
    )

    with freeze_time(NOW), patch("tasks.account_link_notifications.publish_to_mailer") as mock_publish:
        AccountLinkNotificationsTask.notify()

    mock_publish.assert_called_once()
    _, kwargs = mock_publish.call_args
    assert kwargs["data"]["accountId"] == source_org.id
    assert kwargs["data"]["serviceProviderName"] == vendor_org.name
    assert kwargs["data"]["isReminder"] is True
    assert kwargs["data"]["linkDate"] == CREATED_ON_PACIFIC_ISO
    assert kwargs["data"]["expiryDate"] == EXPIRES_ON_30_DAYS_PACIFIC_ISO
    assert key.status == LinkingKeyStatus.ACTIVE.value


def test_expired_key_sends_expiry_notice_and_updates_status(session, app):
    """Assert that a key past its expiry is marked EXPIRED and sends a non-reminder notice."""
    source_org = _factory_org("Source Org")
    vendor_org = _factory_org("Vendor Org")
    key = _factory_linking_key(source_org.id, vendor_org.id, LinkingKeyStatus.ACTIVE.value, EXPIRES_ON_PAST, CREATED_ON)

    with freeze_time(NOW), patch("tasks.account_link_notifications.publish_to_mailer") as mock_publish:
        AccountLinkNotificationsTask.notify()

    mock_publish.assert_called_once()
    _, kwargs = mock_publish.call_args
    assert kwargs["data"]["accountId"] == source_org.id
    assert kwargs["data"]["isReminder"] is False
    assert kwargs["data"]["linkDate"] == CREATED_ON_PACIFIC_ISO
    assert kwargs["data"]["expiryDate"] == EXPIRES_ON_PAST_PACIFIC_ISO
    assert key.status == LinkingKeyStatus.EXPIRED.value


def test_key_not_near_expiry_is_untouched(session, app):
    """Assert that a key expiring well outside the reminder window is left alone."""
    source_org = _factory_org("Source Org")
    vendor_org = _factory_org("Vendor Org")
    key = _factory_linking_key(
        source_org.id, vendor_org.id, LinkingKeyStatus.ACTIVE.value, EXPIRES_IN_FUTURE, CREATED_ON
    )

    with freeze_time(NOW), patch("tasks.account_link_notifications.publish_to_mailer") as mock_publish:
        AccountLinkNotificationsTask.notify()

    mock_publish.assert_not_called()
    assert key.status == LinkingKeyStatus.ACTIVE.value


def test_revoked_expired_key_is_excluded(session, app):
    """Assert that REVOKED/EXPIRED keys are excluded from both queries even if the expiry date matches."""
    source_org = _factory_org("Source Org")
    vendor_org = _factory_org("Vendor Org")
    revoked_key = _factory_linking_key(
        source_org.id, vendor_org.id, LinkingKeyStatus.REVOKED.value, EXPIRES_ON_PAST, CREATED_ON
    )
    expired_key = _factory_linking_key(
        source_org.id, vendor_org.id, LinkingKeyStatus.EXPIRED.value, EXPIRES_ON_PAST, CREATED_ON
    )

    with freeze_time(NOW), patch("tasks.account_link_notifications.publish_to_mailer") as mock_publish:
        AccountLinkNotificationsTask.notify()

    mock_publish.assert_not_called()
    assert revoked_key.status == LinkingKeyStatus.REVOKED.value
    assert expired_key.status == LinkingKeyStatus.EXPIRED.value

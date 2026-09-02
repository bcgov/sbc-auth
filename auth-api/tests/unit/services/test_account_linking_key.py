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
"""Tests for the AccountLinkingKey service."""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
from sbc_common_components.utils.enums import QueueMessageTypes

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.account_linking_key import AccountLinkingKey as AccountLinkingKeyModel
from auth_api.services.account_linking_key import AccountLinkingKey as AccountLinkingKeyService
from auth_api.services.activity_log_publisher import ActivityLogPublisher
from auth_api.utils.enums import ActivityAction, LinkingKeyStatus
from tests.utilities.factory_utils import (
    factory_linking_key_model,
    factory_org_model,
    factory_redirect_url_model,
)

_REDIRECT_URL = "https://vendor.example.com/callback"
_REDIRECT_URL_WILDCARD = "https://vendor.example.com/callback/*"


def test_generate_creates_key(session):  # pylint:disable=unused-argument
    """Assert that generate creates a new active key bound to a vendor."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL)

    record = AccountLinkingKeyService.generate(lawfirm.id, vendor.id, _REDIRECT_URL)

    assert record.id is not None
    assert record.linking_key
    assert record.account_id == lawfirm.id
    assert record.vendor_account_id == vendor.id
    assert record.status == LinkingKeyStatus.ACTIVE.value
    assert record.expires_on > datetime.now(UTC)
    assert record.last_used is None
    assert record.redirect_url == _REDIRECT_URL


def test_generate_with_vendor_binds_immediately(session):  # pylint:disable=unused-argument
    """Assert that vendor_account_id is set at generation."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL)

    record = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id, redirect_url=_REDIRECT_URL)

    assert record.vendor_account_id == vendor.id


def test_generate_for_same_vendor_revokes_previous(session):  # pylint:disable=unused-argument
    """Assert that regenerating for the same vendor revokes the old key."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL)

    first = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id, redirect_url=_REDIRECT_URL)
    first_key = first.linking_key

    second = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id, redirect_url=_REDIRECT_URL)

    assert second.linking_key != first_key
    assert second.status == LinkingKeyStatus.ACTIVE.value

    old = AccountLinkingKeyModel.query.filter_by(linking_key=first_key).one()
    assert old.status == LinkingKeyStatus.REVOKED.value


def test_generate_different_vendors_coexist(session):  # pylint:disable=unused-argument
    """Assert that generating keys for different vendors leaves both active."""
    lawfirm = factory_org_model()
    vendor_a = factory_org_model()
    vendor_b = factory_org_model()
    factory_redirect_url_model(org_id=vendor_a.id, redirect_url=_REDIRECT_URL)
    factory_redirect_url_model(org_id=vendor_b.id, redirect_url=_REDIRECT_URL)

    key_a = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor_a.id, redirect_url=_REDIRECT_URL)
    key_b = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor_b.id, redirect_url=_REDIRECT_URL)

    assert key_a.status == LinkingKeyStatus.ACTIVE.value
    assert key_b.status == LinkingKeyStatus.ACTIVE.value
    assert key_a.linking_key != key_b.linking_key

    active = AccountLinkingKeyModel.find_by_account_id(lawfirm.id)
    assert len(active) == 2


def test_generate_without_vendor_leaves_redirect_url_unset(session):  # pylint:disable=unused-argument
    """Assert that a PENDING key created without a vendor has no redirect_url persisted."""
    lawfirm = factory_org_model()

    record = AccountLinkingKeyService.generate(lawfirm.id)

    assert record.redirect_url is None


def test_generate_vendor_without_redirect_url_rejected(session):  # pylint:disable=unused-argument
    """Assert that vendor_account_id without redirect_url is rejected as a missing redirect URL."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL)

    with pytest.raises(BusinessException) as exc_info:
        AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id)

    assert exc_info.value.code == Error.REDIRECT_URL_REQUIRED.name


def test_generate_redirect_url_without_vendor_rejected(session):  # pylint:disable=unused-argument
    """Assert that redirect_url without vendor_account_id is rejected."""
    lawfirm = factory_org_model()

    with pytest.raises(BusinessException) as exc_info:
        AccountLinkingKeyService.generate(lawfirm.id, redirect_url=_REDIRECT_URL)

    assert exc_info.value.code == Error.VENDOR_ACCOUNT_ID_REQUIRED.name


def test_generate_unregistered_redirect_url_rejected(session):  # pylint:disable=unused-argument
    """Assert that a redirect_url not registered for the vendor is rejected."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL)

    with pytest.raises(BusinessException) as exc_info:
        AccountLinkingKeyService.generate(
            lawfirm.id, vendor_account_id=vendor.id, redirect_url="https://not-registered.example.com/cb"
        )

    assert exc_info.value.code == Error.REDIRECT_URL_INVALID.name


def test_generate_filled_in_wildcard(session):  # pylint:disable=unused-argument
    """Assert that a concrete path matching a registered wildcard is accepted at generation."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL_WILDCARD)

    record = AccountLinkingKeyService.generate(
        lawfirm.id, vendor_account_id=vendor.id, redirect_url="https://vendor.example.com/callback/abc123"
    )

    assert record.redirect_url == "https://vendor.example.com/callback/abc123"


def test_generate_wildcard_matches_bare_boundary(session):  # pylint:disable=unused-argument
    """Assert that the wildcard's own path boundary is accepted at generation."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL_WILDCARD)

    record = AccountLinkingKeyService.generate(
        lawfirm.id, vendor_account_id=vendor.id, redirect_url="https://vendor.example.com/callback/"
    )

    assert record.redirect_url == "https://vendor.example.com/callback/"


def test_generate_persists_query_string_on_wildcard_fill(session):  # pylint:disable=unused-argument
    """Assert that query params tacked on at generation survive into the persisted URL.

    The vendor needs them passed back, and storing them verbatim is what makes the record
    an audit of exactly what came in.
    """
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL_WILDCARD)
    passed = "https://vendor.example.com/callback/abc123?state=xyz&code=123"

    record = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id, redirect_url=passed)

    assert record.redirect_url == passed


def test_generate_persists_query_string_on_exact_match(session):  # pylint:disable=unused-argument
    """Assert that a query string is ignored for matching but retained on an exact registration."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL)
    passed = f"{_REDIRECT_URL}?state=xyz"

    record = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id, redirect_url=passed)

    assert record.redirect_url == passed


@pytest.mark.parametrize(
    "redirect_url",
    [
        "https://vendor.example.com/callback-other/x",
        "https://vendor.example.com/callback/<script>alert(1)</script>",
        "https://vendor.example.com/callback/../../admin",
    ],
)
def test_generate_rejects_url_failing_wildcard_validation(session, redirect_url):  # pylint:disable=unused-argument
    """Assert that a wildcard registration does not let a sibling path, markup or traversal through."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL_WILDCARD)

    with pytest.raises(BusinessException) as exc_info:
        AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id, redirect_url=redirect_url)

    assert exc_info.value.code == Error.REDIRECT_URL_INVALID.name


def test_generate_rejected_attempt_does_not_revoke_existing_key(session):  # pylint:disable=unused-argument
    """Assert that a rejected generate() call leaves an existing key untouched."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL)

    existing = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id, redirect_url=_REDIRECT_URL)

    with pytest.raises(BusinessException):
        AccountLinkingKeyService.generate(
            lawfirm.id, vendor_account_id=vendor.id, redirect_url="https://not-registered.example.com/cb"
        )

    unchanged = AccountLinkingKeyModel.query.get(existing.id)
    assert unchanged.status == LinkingKeyStatus.ACTIVE.value


def test_get_all_returns_active_keys(session):  # pylint:disable=unused-argument
    """Assert that get_all returns only active keys."""
    org = factory_org_model()
    factory_linking_key_model(account_id=org.id)
    factory_linking_key_model(account_id=org.id, status=LinkingKeyStatus.REVOKED.value)

    result = AccountLinkingKeyService.get_all(org.id)
    assert len(result) == 1
    assert result[0].status == LinkingKeyStatus.ACTIVE.value


def test_revoke_sets_status_to_revoked(session):  # pylint:disable=unused-argument
    """Assert that revoke changes the key status to REVOKED."""
    org = factory_org_model()
    vendor = factory_org_model()
    record = factory_linking_key_model(account_id=org.id, vendor_account_id=vendor.id)

    found = AccountLinkingKeyService.revoke(record.id, org.id)

    assert found is True
    updated = AccountLinkingKeyModel.query.get(record.id)
    assert updated.status == LinkingKeyStatus.REVOKED.value


def test_revoke_wrong_org_returns_false(session):  # pylint:disable=unused-argument
    """Assert that revoking a key with the wrong org_id returns False (ownership check)."""
    org_a = factory_org_model()
    org_b = factory_org_model()
    record = factory_linking_key_model(account_id=org_b.id)

    found = AccountLinkingKeyService.revoke(record.id, org_a.id)

    assert found is False
    unchanged = AccountLinkingKeyModel.query.get(record.id)
    assert unchanged.status == LinkingKeyStatus.ACTIVE.value


def test_revoke_nonexistent_returns_false(session):  # pylint:disable=unused-argument
    """Assert that revoking a non-existent key returns False without raising."""
    org = factory_org_model()
    found = AccountLinkingKeyService.revoke(99999, org.id)
    assert found is False


def test_validate_succeeds(session):  # pylint:disable=unused-argument
    """Assert that a valid key returns the linking record."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    record = factory_linking_key_model(account_id=lawfirm.id, vendor_account_id=vendor.id)

    result = AccountLinkingKeyService.validate(record.linking_key, vendor.id)

    assert result is not None
    assert result.account_id == lawfirm.id


def test_validate_rejects_wrong_vendor(session):  # pylint:disable=unused-argument
    """Assert that a vendor other than the bound one is rejected."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    other_vendor = factory_org_model()
    record = factory_linking_key_model(account_id=lawfirm.id, vendor_account_id=vendor.id)

    result = AccountLinkingKeyService.validate(record.linking_key, other_vendor.id)

    assert result is None


def test_validate_rejects_expired_key(session):  # pylint:disable=unused-argument
    """Assert that an expired key is rejected."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    expired = factory_linking_key_model(
        account_id=lawfirm.id,
        vendor_account_id=vendor.id,
        expires_on=datetime.now(UTC) - timedelta(days=1),
    )

    result = AccountLinkingKeyService.validate(expired.linking_key, vendor.id)

    assert result is None


def test_validate_rejects_revoked_key(session):  # pylint:disable=unused-argument
    """Assert that a revoked key is rejected."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    record = factory_linking_key_model(
        account_id=lawfirm.id, vendor_account_id=vendor.id, status=LinkingKeyStatus.REVOKED.value
    )

    result = AccountLinkingKeyService.validate(record.linking_key, vendor.id)

    assert result is None


def test_validate_updates_last_used(session):  # pylint:disable=unused-argument
    """Assert that last_used is updated on each successful validation."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    record = factory_linking_key_model(account_id=lawfirm.id, vendor_account_id=vendor.id)
    assert record.last_used is None

    AccountLinkingKeyService.validate(record.linking_key, vendor.id)

    updated = AccountLinkingKeyModel.query.get(record.id)
    assert updated.last_used is not None


@freeze_time("2026-07-01 12:00:00+00:00")
def test_generate_with_vendor_publishes_link_created(session):  # pylint:disable=unused-argument
    """Assert that generating an immediately-active key publishes an ACCOUNT_LINK_CREATED notification."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    factory_redirect_url_model(org_id=vendor.id, redirect_url=_REDIRECT_URL)

    with patch("auth_api.services.account_linking_key.publish_to_mailer") as mock_publish:
        record = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id, redirect_url=_REDIRECT_URL)

    mock_publish.assert_called_once()
    notification_type, kwargs = mock_publish.call_args.args[0], mock_publish.call_args.kwargs
    assert notification_type == QueueMessageTypes.ACCOUNT_LINK_CREATED.value
    assert kwargs["data"]["accountId"] == lawfirm.id
    assert kwargs["data"]["serviceProviderName"] == vendor.name
    assert kwargs["data"]["linkDate"] == "2026-07-01"
    assert kwargs["data"]["expiryDate"] == "2027-07-01"
    assert record.status == LinkingKeyStatus.ACTIVE.value


def test_generate_without_vendor_does_not_publish(session):  # pylint:disable=unused-argument
    """Assert that generating a PENDING key does not publish a mailer notification."""
    lawfirm = factory_org_model()

    with patch("auth_api.services.account_linking_key.publish_to_mailer") as mock_publish:
        AccountLinkingKeyService.generate(lawfirm.id)

    mock_publish.assert_not_called()


@freeze_time("2026-07-01 12:00:00+00:00")
def test_bind_publishes_link_created(session):  # pylint:disable=unused-argument
    """Assert that binding a PENDING key publishes an ACCOUNT_LINK_CREATED notification."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    pending_key = factory_linking_key_model(account_id=lawfirm.id, status=LinkingKeyStatus.PENDING.value)

    with patch("auth_api.services.account_linking_key.publish_to_mailer") as mock_publish:
        record = AccountLinkingKeyService.bind(pending_key.linking_key, vendor.id)

    mock_publish.assert_called_once()
    notification_type, kwargs = mock_publish.call_args.args[0], mock_publish.call_args.kwargs
    assert notification_type == QueueMessageTypes.ACCOUNT_LINK_CREATED.value
    assert kwargs["data"]["accountId"] == lawfirm.id
    assert kwargs["data"]["serviceProviderName"] == vendor.name
    assert kwargs["data"]["linkDate"] == "2026-07-01"
    assert kwargs["data"]["expiryDate"] == "2027-07-01"
    assert record.status == LinkingKeyStatus.ACTIVE.value


@freeze_time("2026-07-01 12:00:00+00:00")
def test_revoke_active_key_publishes_link_removed(session):  # pylint:disable=unused-argument
    """Assert that revoking an ACTIVE key publishes an ACCOUNT_LINK_REMOVED notification."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    record = factory_linking_key_model(account_id=lawfirm.id, vendor_account_id=vendor.id)

    with patch("auth_api.services.account_linking_key.publish_to_mailer") as mock_publish:
        found = AccountLinkingKeyService.revoke(record.id, lawfirm.id)

    assert found is True
    mock_publish.assert_called_once()
    notification_type, kwargs = mock_publish.call_args.args[0], mock_publish.call_args.kwargs
    assert notification_type == QueueMessageTypes.ACCOUNT_LINK_REMOVED.value
    assert kwargs["data"]["accountId"] == lawfirm.id
    assert kwargs["data"]["serviceProviderName"] == vendor.name
    assert kwargs["data"]["linkRemovalDate"] == "2026-07-01"


def test_revoke_pending_key_does_not_publish(session):  # pylint:disable=unused-argument
    """Assert that revoking a PENDING key (never active) does not publish a mailer notification."""
    lawfirm = factory_org_model()
    record = factory_linking_key_model(account_id=lawfirm.id, status=LinkingKeyStatus.PENDING.value)

    with patch("auth_api.services.account_linking_key.publish_to_mailer") as mock_publish:
        found = AccountLinkingKeyService.revoke(record.id, lawfirm.id)

    assert found is True
    mock_publish.assert_not_called()


def test_extend_moves_expiry_one_year_from_original(session):  # pylint:disable=unused-argument
    """Assert that extend adds a year to the existing expiry, not to today."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    original_expiry = datetime.now(UTC) + timedelta(days=10)
    record = factory_linking_key_model(account_id=lawfirm.id, vendor_account_id=vendor.id, expires_on=original_expiry)

    updated = AccountLinkingKeyService.extend(record.id, lawfirm.id)

    assert updated is not None
    assert updated.expires_on == original_expiry + relativedelta(years=1)


def test_extend_allowed_on_the_thirtieth_day(session):  # pylint:disable=unused-argument
    """Assert that the eligibility window is inclusive of the 30th day before expiry."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    record = factory_linking_key_model(
        account_id=lawfirm.id,
        vendor_account_id=vendor.id,
        expires_on=datetime.now(UTC) + timedelta(days=30) - timedelta(minutes=1),
    )

    assert AccountLinkingKeyService.extend(record.id, lawfirm.id) is not None


def test_extend_rejected_outside_the_window(session):  # pylint:disable=unused-argument
    """Assert that a key more than 30 days from expiry cannot be extended."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    record = factory_linking_key_model(
        account_id=lawfirm.id, vendor_account_id=vendor.id, expires_on=datetime.now(UTC) + timedelta(days=31)
    )

    with pytest.raises(BusinessException) as exc_info:
        AccountLinkingKeyService.extend(record.id, lawfirm.id)

    assert exc_info.value.code == Error.LINKING_KEY_NOT_NEAR_EXPIRY.name


def test_extend_allowed_when_past_expiry_but_not_yet_swept(session):  # pylint:disable=unused-argument
    """Assert that a key past its expiry is still extendable while auth-jobs has not run yet."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    original_expiry = datetime.now(UTC) - timedelta(days=2)
    record = factory_linking_key_model(account_id=lawfirm.id, vendor_account_id=vendor.id, expires_on=original_expiry)

    updated = AccountLinkingKeyService.extend(record.id, lawfirm.id)

    assert updated is not None
    assert updated.expires_on == original_expiry + relativedelta(years=1)


def test_extend_rejects_pending_key(session):  # pylint:disable=unused-argument
    """Assert that an unbound PENDING key cannot be extended."""
    lawfirm = factory_org_model()
    record = factory_linking_key_model(
        account_id=lawfirm.id, status=LinkingKeyStatus.PENDING.value, expires_on=datetime.now(UTC) + timedelta(days=5)
    )

    with pytest.raises(BusinessException) as exc_info:
        AccountLinkingKeyService.extend(record.id, lawfirm.id)

    assert exc_info.value.code == Error.INVALID_LINKING_KEY_STATE.name


def test_extend_revoked_key_returns_none(session):  # pylint:disable=unused-argument
    """Assert that a REVOKED key is not found by extend."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    record = factory_linking_key_model(
        account_id=lawfirm.id, vendor_account_id=vendor.id, status=LinkingKeyStatus.REVOKED.value
    )

    assert AccountLinkingKeyService.extend(record.id, lawfirm.id) is None


def test_extend_wrong_account_returns_none(session):  # pylint:disable=unused-argument
    """Assert that a key belonging to another account is not found by extend."""
    lawfirm = factory_org_model()
    other = factory_org_model()
    vendor = factory_org_model()
    record = factory_linking_key_model(
        account_id=other.id, vendor_account_id=vendor.id, expires_on=datetime.now(UTC) + timedelta(days=5)
    )

    assert AccountLinkingKeyService.extend(record.id, lawfirm.id) is None


def test_extend_publishes_activity(session):  # pylint:disable=unused-argument
    """Assert that extending logs an activity."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()
    record = factory_linking_key_model(
        account_id=lawfirm.id, vendor_account_id=vendor.id, expires_on=datetime.now(UTC) + timedelta(days=5)
    )

    with patch.object(ActivityLogPublisher, "publish_activity") as mock_activity:
        AccountLinkingKeyService.extend(record.id, lawfirm.id)

    mock_activity.assert_called_once()
    assert mock_activity.call_args.args[0].action == ActivityAction.LINKING_KEY_EXTENDED.value

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

from auth_api.models.account_linking_key import AccountLinkingKey as AccountLinkingKeyModel
from auth_api.services.account_linking_key import AccountLinkingKey as AccountLinkingKeyService
from auth_api.utils.enums import LinkingKeyStatus
from tests.utilities.factory_utils import (
    factory_linking_key_model,
    factory_org_model,
)


def test_generate_creates_key(session):  # pylint:disable=unused-argument
    """Assert that generate creates a new active key bound to a vendor."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()

    record = AccountLinkingKeyService.generate(lawfirm.id, vendor.id)

    assert record.id is not None
    assert record.linking_key
    assert record.account_id == lawfirm.id
    assert record.vendor_account_id == vendor.id
    assert record.status == LinkingKeyStatus.ACTIVE.value
    assert record.expires_on > datetime.now(UTC)
    assert record.last_used is None


def test_generate_with_vendor_binds_immediately(session):  # pylint:disable=unused-argument
    """Assert that vendor_account_id is set at generation."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()

    record = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id)

    assert record.vendor_account_id == vendor.id


def test_generate_for_same_vendor_revokes_previous(session):  # pylint:disable=unused-argument
    """Assert that regenerating for the same vendor revokes the old key."""
    lawfirm = factory_org_model()
    vendor = factory_org_model()

    first = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id)
    first_key = first.linking_key

    second = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor.id)

    assert second.linking_key != first_key
    assert second.status == LinkingKeyStatus.ACTIVE.value

    old = AccountLinkingKeyModel.query.filter_by(linking_key=first_key).one()
    assert old.status == LinkingKeyStatus.REVOKED.value


def test_generate_different_vendors_coexist(session):  # pylint:disable=unused-argument
    """Assert that generating keys for different vendors leaves both active."""
    lawfirm = factory_org_model()
    vendor_a = factory_org_model()
    vendor_b = factory_org_model()

    key_a = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor_a.id)
    key_b = AccountLinkingKeyService.generate(lawfirm.id, vendor_account_id=vendor_b.id)

    assert key_a.status == LinkingKeyStatus.ACTIVE.value
    assert key_b.status == LinkingKeyStatus.ACTIVE.value
    assert key_a.linking_key != key_b.linking_key

    active = AccountLinkingKeyModel.find_active_by_account_id(lawfirm.id)
    assert len(active) == 2


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
    record = factory_linking_key_model(account_id=org.id)

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

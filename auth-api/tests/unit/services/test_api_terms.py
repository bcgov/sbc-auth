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
"""Tests for the ApiTerms service.

Each test publishes the 'k01' termsofuse_api document, so it is the latest version unless a test adds another.
"""

from unittest.mock import patch

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.dataclass import Activity
from auth_api.models.org_api_terms_acceptance import OrgApiTermsAcceptance as OrgApiTermsAcceptanceModel
from auth_api.services.activity_log_publisher import ActivityLogPublisher
from auth_api.services.api_terms import ApiTerms as ApiTermsService
from auth_api.utils.enums import ActivityAction, DocumentType
from tests.utilities.factory_scenarios import TestUserInfo
from tests.utilities.factory_utils import (
    factory_document_model,
    factory_membership_model,
    factory_org_model,
    factory_user_model,
    patch_token_info,
)

_LATEST_VERSION = "k01"


def _setup_account_admin(monkeypatch):
    """Create an org and an admin of it, and use the admin's token."""
    user = factory_user_model(TestUserInfo.user_test)
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    patch_token_info(
        {
            "sub": user.keycloak_guid,
            "idp_userid": user.idp_userid,
            "realm_access": {"roles": ["public_user", "account_holder"]},
        },
        monkeypatch,
    )
    return user, org


def test_accept_latest_version(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that accepting the latest version records the acceptance and logs the activity."""
    factory_document_model(_LATEST_VERSION, DocumentType.TERMS_OF_USE_API.value, "<p>Terms</p>")
    user, org = _setup_account_admin(monkeypatch)

    with patch.object(ActivityLogPublisher, "publish_activity") as mock_activity:
        status = ApiTermsService.accept(org.id, _LATEST_VERSION)

    assert status["isAccepted"] is True
    assert status["acceptedVersionId"] == _LATEST_VERSION
    assert status["acceptedBy"] == user.username
    assert status["acceptedOn"]
    record = OrgApiTermsAcceptanceModel.find_by_org_and_version(org.id, _LATEST_VERSION)
    assert record.created_by_id == user.id
    mock_activity.assert_called_once_with(
        Activity(
            org_id=org.id,
            action=ActivityAction.API_TERMS_ACCEPTED.value,
            name=org.name,
            value=_LATEST_VERSION,
            id=record.id,
        )
    )
    assert ApiTermsService.get_status(org.id) == status
    assert ApiTermsService.is_latest_accepted(org.id) is True


def test_accept_version_mismatch(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that accepting a version other than the latest is rejected and nothing is recorded."""
    factory_document_model(_LATEST_VERSION, DocumentType.TERMS_OF_USE_API.value, "<p>Terms</p>")
    _, org = _setup_account_admin(monkeypatch)
    factory_document_model("k02", DocumentType.TERMS_OF_USE_API.value, "<p>Updated terms</p>")

    with patch.object(ActivityLogPublisher, "publish_activity") as mock_activity:
        with pytest.raises(BusinessException) as exc_info:
            ApiTermsService.accept(org.id, _LATEST_VERSION)

    assert exc_info.value.code == Error.API_TERMS_VERSION_MISMATCH.name
    assert OrgApiTermsAcceptanceModel.find_latest_by_org(org.id) is None
    mock_activity.assert_not_called()


def test_accept_older_version_is_not_latest_accepted(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an acceptance of an older version doesn't count once a newer version is published."""
    factory_document_model(_LATEST_VERSION, DocumentType.TERMS_OF_USE_API.value, "<p>Terms</p>")
    _, org = _setup_account_admin(monkeypatch)
    with patch.object(ActivityLogPublisher, "publish_activity"):
        ApiTermsService.accept(org.id, _LATEST_VERSION)

    factory_document_model("k02", DocumentType.TERMS_OF_USE_API.value, "<p>Updated terms</p>")

    status = ApiTermsService.get_status(org.id)
    assert status["isAccepted"] is False
    assert status["acceptedVersionId"] == _LATEST_VERSION
    assert ApiTermsService.is_latest_accepted(org.id) is False


def test_accept_twice(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that accepting the same version again is a no-op that returns the existing acceptance."""
    factory_document_model(_LATEST_VERSION, DocumentType.TERMS_OF_USE_API.value, "<p>Terms</p>")
    _, org = _setup_account_admin(monkeypatch)

    with patch.object(ActivityLogPublisher, "publish_activity") as mock_activity:
        first = ApiTermsService.accept(org.id, _LATEST_VERSION)
        second = ApiTermsService.accept(org.id, _LATEST_VERSION)

    assert second == first
    assert OrgApiTermsAcceptanceModel.query.filter_by(org_id=org.id).count() == 1
    mock_activity.assert_called_once()


def test_accept_concurrent_duplicate(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that losing a race to record the same acceptance is treated as already accepted."""
    factory_document_model(_LATEST_VERSION, DocumentType.TERMS_OF_USE_API.value, "<p>Terms</p>")
    _, org = _setup_account_admin(monkeypatch)
    with patch.object(ActivityLogPublisher, "publish_activity"):
        ApiTermsService.accept(org.id, _LATEST_VERSION)
    existing = OrgApiTermsAcceptanceModel.find_by_org_and_version(org.id, _LATEST_VERSION)

    # simulate a concurrent request that inserted the row after this request checked for it
    with (
        patch.object(OrgApiTermsAcceptanceModel, "find_by_org_and_version", side_effect=[None, existing]),
        patch.object(ActivityLogPublisher, "publish_activity") as mock_activity,
    ):
        status = ApiTermsService.accept(org.id, _LATEST_VERSION)

    assert status["acceptedVersionId"] == _LATEST_VERSION
    assert OrgApiTermsAcceptanceModel.query.filter_by(org_id=org.id).count() == 1
    mock_activity.assert_not_called()


def test_no_terms_document(session, monkeypatch):  # pylint:disable=unused-argument
    """Assert that with no terms document the terms can't be accepted and key creation is blocked."""
    _, org = _setup_account_admin(monkeypatch)

    # the terms page already loaded the document, so a missing one is reported as a version mismatch
    with pytest.raises(BusinessException) as exc_info:
        ApiTermsService.accept(org.id, _LATEST_VERSION)
    assert exc_info.value.code == Error.API_TERMS_VERSION_MISMATCH.name

    assert ApiTermsService.get_status(org.id)["isAccepted"] is False
    with pytest.raises(BusinessException) as exc_info:
        ApiTermsService.is_latest_accepted(org.id)
    assert exc_info.value.code == Error.API_TERMS_NOT_FOUND.name

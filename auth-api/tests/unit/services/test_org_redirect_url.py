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
"""Tests for the OrgRedirectUrl service."""

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.org_redirect_url import OrgRedirectUrl as OrgRedirectUrlModel
from auth_api.services.org_redirect_url import OrgRedirectUrl as OrgRedirectUrlService
from tests.utilities.factory_utils import (
    factory_org_model,
    factory_redirect_url_model,
)


def test_create_adds_url(session):  # pylint:disable=unused-argument
    """Assert that create adds a new redirect URL for the org."""
    org = factory_org_model()

    record = OrgRedirectUrlService.create(org.id, "https://vendor.example.com/callback")

    assert record.id is not None
    assert record.org_id == org.id
    assert record.redirect_url == "https://vendor.example.com/callback"


def test_create_trims_whitespace(session):  # pylint:disable=unused-argument
    """Assert that leading/trailing whitespace is trimmed before save."""
    org = factory_org_model()

    record = OrgRedirectUrlService.create(org.id, "  https://vendor.example.com/callback  ")

    assert record.redirect_url == "https://vendor.example.com/callback"


def test_create_rejects_empty_url(session):  # pylint:disable=unused-argument
    """Assert that an empty URL is rejected."""
    org = factory_org_model()

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.create(org.id, "   ")

    assert exc_info.value.code == Error.REDIRECT_URL_REQUIRED.name


def test_create_rejects_invalid_url(session):  # pylint:disable=unused-argument
    """Assert that a non-http(s) URL is rejected."""
    org = factory_org_model()

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.create(org.id, "not-a-url")

    assert exc_info.value.code == Error.INVALID_REDIRECT_URL.name


def test_create_allows_trailing_wildcard(session):  # pylint:disable=unused-argument
    """Assert that a trailing /* wildcard is accepted."""
    org = factory_org_model()

    record = OrgRedirectUrlService.create(org.id, "https://vendor.example.com/callback/*")

    assert record.redirect_url == "https://vendor.example.com/callback/*"


def test_create_rejects_wildcard_not_at_end(session):  # pylint:disable=unused-argument
    """Assert that a wildcard anywhere other than the trailing path segment is rejected."""
    org = factory_org_model()

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.create(org.id, "https://vendor.example.com/*/callback")

    assert exc_info.value.code == Error.INVALID_REDIRECT_URL.name


def test_create_rejects_url_with_query_string(session):  # pylint:disable=unused-argument
    """Assert that a URL carrying a query string is rejected."""
    org = factory_org_model()

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.create(org.id, "https://vendor.example.com/callback?ref=abc")

    assert exc_info.value.code == Error.INVALID_REDIRECT_URL.name


def test_create_rejects_url_with_fragment(session):  # pylint:disable=unused-argument
    """Assert that a URL carrying a fragment is rejected."""
    org = factory_org_model()

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.create(org.id, "https://vendor.example.com/callback#section")

    assert exc_info.value.code == Error.INVALID_REDIRECT_URL.name


def test_create_rejects_duplicate_url(session):  # pylint:disable=unused-argument
    """Assert that duplicate URLs for the same org are rejected."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback")

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.create(org.id, "https://vendor.example.com/callback")

    assert exc_info.value.code == Error.REDIRECT_URL_ALREADY_EXISTS.name


def test_create_allows_same_url_for_different_orgs(session):  # pylint:disable=unused-argument
    """Assert that the same URL can be registered by different orgs."""
    org_a = factory_org_model()
    org_b = factory_org_model()
    factory_redirect_url_model(org_id=org_a.id, redirect_url="https://vendor.example.com/callback")

    record = OrgRedirectUrlService.create(org_b.id, "https://vendor.example.com/callback")

    assert record.org_id == org_b.id


def test_get_all_returns_org_urls(session):  # pylint:disable=unused-argument
    """Assert that get_all returns only the urls owned by the org."""
    org_a = factory_org_model()
    org_b = factory_org_model()
    factory_redirect_url_model(org_id=org_a.id, redirect_url="https://vendor.example.com/one")
    factory_redirect_url_model(org_id=org_a.id, redirect_url="https://vendor.example.com/two")
    factory_redirect_url_model(org_id=org_b.id, redirect_url="https://other.example.com/one")

    result = OrgRedirectUrlService.get_all(org_a.id)

    assert len(result) == 2
    assert {r.redirect_url for r in result} == {
        "https://vendor.example.com/one",
        "https://vendor.example.com/two",
    }


def test_update_changes_url(session):  # pylint:disable=unused-argument
    """Assert that update changes the redirect URL value."""
    org = factory_org_model()
    record = factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/old")

    updated = OrgRedirectUrlService.update(record.id, org.id, "https://vendor.example.com/new")

    assert updated.redirect_url == "https://vendor.example.com/new"


def test_update_rejects_invalid_url(session):  # pylint:disable=unused-argument
    """Assert that update rejects an invalid URL and leaves the record unchanged."""
    org = factory_org_model()
    record = factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/old")

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.update(record.id, org.id, "not-a-url")

    assert exc_info.value.code == Error.INVALID_REDIRECT_URL.name
    unchanged = OrgRedirectUrlModel.query.get(record.id)
    assert unchanged.redirect_url == "https://vendor.example.com/old"


def test_update_rejects_duplicate_of_another_row(session):  # pylint:disable=unused-argument
    """Assert that update rejects a value that duplicates another row for the same org."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/existing")
    record = factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/old")

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.update(record.id, org.id, "https://vendor.example.com/existing")

    assert exc_info.value.code == Error.REDIRECT_URL_ALREADY_EXISTS.name


def test_update_allows_saving_unchanged_value(session):  # pylint:disable=unused-argument
    """Assert that saving the same value back on the same row is not treated as a duplicate."""
    org = factory_org_model()
    record = factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/same")

    updated = OrgRedirectUrlService.update(record.id, org.id, "https://vendor.example.com/same")

    assert updated.redirect_url == "https://vendor.example.com/same"


def test_update_wrong_org_returns_none(session):  # pylint:disable=unused-argument
    """Assert that updating a url scoped to a different org returns None."""
    org_a = factory_org_model()
    org_b = factory_org_model()
    record = factory_redirect_url_model(org_id=org_b.id)

    updated = OrgRedirectUrlService.update(record.id, org_a.id, "https://vendor.example.com/new")

    assert updated is None


def test_delete_removes_url(session):  # pylint:disable=unused-argument
    """Assert that delete removes the redirect URL row."""
    org = factory_org_model()
    record = factory_redirect_url_model(org_id=org.id)

    found = OrgRedirectUrlService.delete(record.id, org.id)

    assert found is True
    assert OrgRedirectUrlModel.query.get(record.id) is None


def test_delete_wrong_org_returns_false(session):  # pylint:disable=unused-argument
    """Assert that deleting a url scoped to a different org returns False."""
    org_a = factory_org_model()
    org_b = factory_org_model()
    record = factory_redirect_url_model(org_id=org_b.id)

    found = OrgRedirectUrlService.delete(record.id, org_a.id)

    assert found is False
    assert OrgRedirectUrlModel.query.get(record.id) is not None


def test_delete_nonexistent_returns_false(session):  # pylint:disable=unused-argument
    """Assert that deleting a non-existent url returns False without raising."""
    org = factory_org_model()
    found = OrgRedirectUrlService.delete(99999, org.id)
    assert found is False


def test_is_valid_redirect_url_true_for_registered_url(session):  # pylint:disable=unused-argument
    """Assert that a registered URL is considered valid."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback")

    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, "https://vendor.example.com/callback") is True


def test_is_valid_redirect_url_false_for_unregistered_url(session):  # pylint:disable=unused-argument
    """Assert that an unregistered URL is not considered valid."""
    org = factory_org_model()

    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, "https://vendor.example.com/unknown") is False


def test_is_valid_redirect_url_matches_wildcard_prefix(session):  # pylint:disable=unused-argument
    """Assert that a registered wildcard URL matches any URL sharing its path prefix."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback/*")

    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, "https://vendor.example.com/callback/success") is True
    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, "https://vendor.example.com/callback/abc/123") is True


def test_is_valid_redirect_url_wildcard_does_not_match_other_prefix(session):  # pylint:disable=unused-argument
    """Assert that a registered wildcard URL does not match a different path prefix."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback/*")

    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, "https://vendor.example.com/other/success") is False


def test_is_valid_redirect_url_ignores_query_string(session):  # pylint:disable=unused-argument
    """Assert that a query string on the incoming URL does not affect matching."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback")

    assert (
        OrgRedirectUrlService.is_valid_redirect_url(org.id, "https://vendor.example.com/callback?ref=abc&x=1") is True
    )


def test_is_valid_redirect_url_ignores_fragment(session):  # pylint:disable=unused-argument
    """Assert that a fragment on the incoming URL does not affect matching."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback")

    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, "https://vendor.example.com/callback#section") is True


def test_is_valid_redirect_url_wildcard_ignores_query_string(session):  # pylint:disable=unused-argument
    """Assert that a wildcard match also ignores the query string on the incoming URL."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback/*")

    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, "https://vendor.example.com/callback/ok?ref=abc") is True


def test_is_valid_redirect_url_does_not_match_sibling_path(session):  # pylint:disable=unused-argument
    """Assert that a registered URL does not match a path that merely starts with it."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback")

    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, "https://vendor.example.com/callback-other") is False


def test_is_valid_redirect_url_wildcard_does_not_match_sibling_path(session):  # pylint:disable=unused-argument
    """Assert that the trailing slash in a wildcard acts as a path boundary."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback/*")

    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, "https://vendor.example.com/callback-other/x") is False


@pytest.mark.parametrize(
    "url",
    [
        "https://vendor.example.com/<script>alert('xss')</script>",
        "https://vendor.example.com/callback🎉",
        "https://vendor.example.com/call back",
        'https://vendor.example.com/"quoted"',
        "https://vendor.example.com/call\nback",
        "https://vendor.example.com/callback\r\nLocation: https://bad.example.com",
        "https://vendor.example.com/call%20back",
        "https://vendor.example.com/%3Cscript%3Ealert(1)%3C/script%3E",
        "https://vendor.example.com/callback@v2",
        "https://vendor.example.com/callback,extra",
        "https://vendor.example.com/callback;a=abc",
    ],
)
def test_create_rejects_url_with_disallowed_path_characters(session, url):  # pylint:disable=unused-argument
    """Assert that a path outside the allowed character set is rejected, percent-encoding included."""
    org = factory_org_model()

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.create(org.id, url)

    assert exc_info.value.code == Error.INVALID_REDIRECT_URL.name


def test_create_rejects_userinfo_in_host(session):  # pylint:disable=unused-argument
    """Assert that a host carrying userinfo is rejected — it reads as the trusted host but is not."""
    org = factory_org_model()

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.create(org.id, "https://vendor.example.com@bad.example.com/callback")

    assert exc_info.value.code == Error.INVALID_REDIRECT_URL.name


def test_create_allows_host_with_port(session):  # pylint:disable=unused-argument
    """Assert that a host carrying a port is accepted."""
    org = factory_org_model()

    record = OrgRedirectUrlService.create(org.id, "https://vendor.example.com:8443/callback")

    assert record.redirect_url == "https://vendor.example.com:8443/callback"


def test_create_rejects_http_scheme(session):  # pylint:disable=unused-argument
    """Assert that http is rejected — redirecting a user over plaintext is a downgrade."""
    org = factory_org_model()

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.create(org.id, "http://vendor.example.com/callback")

    assert exc_info.value.code == Error.INVALID_REDIRECT_URL.name


@pytest.mark.parametrize(
    "url",
    [
        "https://vendor.example.com/callback/<script>alert('xss')</script>",
        "https://vendor.example.com/callback/done🎉",
        "https://vendor.example.com/callback/done\r\nLocation: https://bad.example.com",
        "https://vendor.example.com/callback/%20ok",
        "https://vendor.example.com/callback/ok;a=abc",
    ],
)
def test_is_valid_redirect_url_rejects_disallowed_characters_via_wildcard(session, url):  # pylint:disable=unused-argument
    """Assert that a wildcard match does not let disallowed characters through the suffix."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback/*")

    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, url) is False


@pytest.mark.parametrize(
    "url",
    [
        "https://vendor.example.com/callback/../../admin",
        "https://vendor.example.com/callback/%2e%2e%2f%2e%2e%2fadmin",
    ],
)
def test_is_valid_redirect_url_rejects_path_traversal_via_wildcard(session, url):  # pylint:disable=unused-argument
    """Assert that traversal cannot escape the path boundary a wildcard is meant to guarantee."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback/*")

    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, url) is False


def test_create_rejects_path_traversal(session):  # pylint:disable=unused-argument
    """Assert that a registered URL cannot contain a traversal segment."""
    org = factory_org_model()

    with pytest.raises(BusinessException) as exc_info:
        OrgRedirectUrlService.create(org.id, "https://vendor.example.com/callback/../admin")

    assert exc_info.value.code == Error.INVALID_REDIRECT_URL.name


def test_is_valid_redirect_url_false_for_empty_url(session):  # pylint:disable=unused-argument
    """Assert that an empty URL is not considered valid."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback")

    assert OrgRedirectUrlService.is_valid_redirect_url(org.id, "") is False


def test_is_valid_redirect_url_still_ignores_encoded_query_string(session):  # pylint:disable=unused-argument
    """Assert that the query string stays exempt — it is dropped before matching."""
    org = factory_org_model()
    factory_redirect_url_model(org_id=org.id, redirect_url="https://vendor.example.com/callback")

    assert (
        OrgRedirectUrlService.is_valid_redirect_url(org.id, "https://vendor.example.com/callback?next=%2Fhome&a=b")
        is True
    )

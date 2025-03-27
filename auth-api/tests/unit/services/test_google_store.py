# Copyright © 2019 Province of British Columbia
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
"""Tests for the Google Store service."""
from datetime import timedelta
from unittest.mock import MagicMock, patch

from auth_api.services import GoogleStoreService


def test_create_signed_put_url(session, gcs_mock):  # pylint:disable=unused-argument
    """Assert that a PUT URL can be pre-signed."""
    file_name = "affidavit-test.pdf"
    signed_url = GoogleStoreService.create_signed_put_url(file_name, prefix_key="Test")

    # Assert the results
    assert signed_url
    assert signed_url["preSignedUrl"] == "http://mocked.url"  # From fixture
    assert signed_url["key"].startswith("Test/")
    assert signed_url["key"].endswith(".pdf")

    # Verify the mocks were called as expected
    gcs_mock["mock_client"].bucket.assert_called_once()
    gcs_mock["mock_bucket"].blob.assert_called_once()
    gcs_mock["mock_blob"].generate_signed_url.assert_called_once_with(
        version="v4",
        expiration=timedelta(minutes=5),  # Keep your expected expiration
        method="PUT",
        content_type="application/octet-stream",
        service_account_email="test@project.iam.gserviceaccount.com",  # From fixture
        access_token="mock-token",  # From fixture
    )


def test_create_signed_get_url(session, tmpdir, gcs_mock):  # pylint:disable=unused-argument
    """Assert that a GET URL can be pre-signed."""
    # Setup mock credentials
    mock_credentials = MagicMock()
    mock_credentials.service_account_email = "test@project.iam.gserviceaccount.com"
    mock_credentials.token = "mock-token"

    with patch("google.auth.compute_engine.Credentials", return_value=mock_credentials):
        # Set up test file
        d = tmpdir.mkdir("subdir")
        fh = d.join("test-file.txt")
        fh.write("Test File")
        file_name = fh.basename

        # Get the mocked GCS objects
        mock_client = gcs_mock["mock_client"]
        mock_bucket = gcs_mock["mock_bucket"]
        mock_blob = gcs_mock["mock_blob"]

        # Mock the signed URLs
        mock_blob.generate_signed_url.side_effect = [
            "http://mocked-put-url",  # Signed PUT URL
            "http://mocked-get-url",  # Signed GET URL
        ]

        # Test PUT URL
        signed_url = GoogleStoreService.create_signed_put_url(file_name, prefix_key="Test")
        key = signed_url.get("key")

        # Test GET URL
        pre_signed_get = GoogleStoreService.create_signed_get_url(key)

        # Verify results
        assert pre_signed_get == "http://mocked-get-url"
        assert mock_client.bucket.call_count == 2
        mock_bucket.blob.assert_any_call(key)

        # Verify GET URL call
        mock_blob.generate_signed_url.assert_any_call(
            version="v4",
            expiration=timedelta(hours=1),
            method="GET",
            service_account_email="test@project.iam.gserviceaccount.com",
            access_token="mock-token",
        )

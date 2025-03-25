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
"""Tests for the Google Store  service.

Test suite to ensure that the Google Store service routines are working as expected.
"""

from datetime import timedelta

from auth_api.services import GoogleStoreService


def test_create_signed_put_url(session, gcs_mock):  # pylint:disable=unused-argument
    """Assert that a PUT URL can be pre-signed."""
    file_name = "affidavit-test.pdf"
    signed_url = GoogleStoreService.create_signed_put_url(file_name, prefix_key="Test")

    # Assert the results
    assert signed_url
    assert signed_url.get("key").startswith("Test/")
    assert signed_url.get("key").endswith(".pdf")

    # Verify the mocks were called as expected
    gcs_mock["mock_client"].bucket.assert_called_once()
    gcs_mock["mock_bucket"].blob.assert_called_once()
    gcs_mock["mock_blob"].generate_signed_url.assert_called_once()


def test_create_signed_get_url(session, tmpdir, gcs_mock):  # pylint:disable=unused-argument
    """Assert that a GET URL can be pre-signed."""
    # Set up a temporary file (if needed for other parts of the test)
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

    # Create a signed PUT URL
    signed_url = GoogleStoreService.create_signed_put_url(file_name, prefix_key="Test")
    key = signed_url.get("key")
    pre_signed_put = signed_url.get("signedUrl")

    # Verify the signed PUT URL
    assert pre_signed_put == "http://mocked-put-url"
    assert key.startswith("Test/")
    assert key.endswith(".txt")

    # Create a signed GET URL
    pre_signed_get = GoogleStoreService.create_signed_get_url(key)

    # Verify the signed GET URL
    assert pre_signed_get == "http://mocked-get-url"

    # Verify the GCS client methods were called as expected
    assert mock_client.bucket.call_count == 2
    mock_client.bucket.assert_any_call("auth-accounts-dev")
    mock_bucket.blob.assert_any_call(key)
    mock_blob.generate_signed_url.assert_any_call(
        version="v4",
        expiration=timedelta(minutes=5),
        method="PUT",
        content_type="application/octet-stream",
    )
    mock_blob.generate_signed_url.assert_any_call(
        version="v4",
        expiration=timedelta(hours=1),
        method="GET",
    )

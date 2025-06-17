# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module for interacting with Google Cloud Storage (GCS)."""

from flask import current_app
from google.cloud import storage


class GoogleStoreService:
    """Document Storage class."""

    @staticmethod
    def download_file_from_bucket(bucket_name: str, source_blob_name: str) -> bytes:
        """
        Download a file from a Google Cloud Storage bucket and return its content as bytes.

        Args:
            bucket_name (str): The name of the bucket.
            source_blob_name (str): The name of the blob (file) in the bucket.

        Returns:
            bytes: The content of the file as bytes.
        """
        client = storage.Client()
        current_app.logger.debug(f"Get bucket file {bucket_name}/{source_blob_name}")
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        file_content = blob.download_as_bytes()
        return file_content

    @staticmethod
    def upload_file_to_bucket(bucket_name, source_file_name, destination_blob_name):
        """
        Upload a file to a specified Google Cloud Storage (GCS) bucket.

        Args:
            bucket_name (str): The name of the GCS bucket where the file will be uploaded.
            source_file_name (str): The local path to the file to be uploaded.
            destination_blob_name (str): The name of the file as it will appear in the GCS bucket.

        Returns:
            None

        Raises:
            google.cloud.exceptions.GoogleCloudError: If an error occurs during the upload process.

        Example:
            >>> GoogleStoreService.upload_file_to_bucket('my-bucket', 'local-file.txt', 'remote-file.txt')
            Upload of remote-file.txt complete.
        """
        client = storage.Client()
        current_app.logger.debug(f"Put bucket file {bucket_name}/{destination_blob_name}")
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        current_app.logger.info("Upload of %s complete.", destination_blob_name)

    @staticmethod
    def get_static_resource_url(key: str) -> str:
        """
        Generate a publicly accessible URL for a file stored in a Google Cloud Storage (GCS) bucket.

        Args:
            key (str): The name or path of the file in the GCS bucket.

        Returns:
            str: A publicly accessible URL for the file.

        Example:
            >>> GoogleStoreService.get_static_resource_url('my-file.txt')
            'https://my-bucket-url/my-file.txt'
        """
        current_app.logger.debug(f"GET URL for {key}")
        bucket_url = current_app.config["STATIC_RESOURCES_BUCKET_URL"]
        return f"https://{bucket_url}/{key}"  # noqa: E231

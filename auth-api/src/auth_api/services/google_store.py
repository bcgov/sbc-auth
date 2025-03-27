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

import uuid
from datetime import timedelta

import google.auth
from flask import current_app
from google.auth.compute_engine import Credentials
from google.auth.transport import requests
from google.cloud import storage
from structured_logging import StructuredLogging

from auth_api.utils.constants import AFFIDAVIT_FOLDER_NAME

logger = StructuredLogging.get_logger()


class GoogleStoreService:
    """Document Storage class."""

    @staticmethod
    def _get_signing_credentials():
        """Get credentials with explicit token refresh.
        Works in both production (GCE) and local development.
        """
        try:
            creds, project = google.auth.default()

            if isinstance(creds, Credentials):
                auth_request = requests.Request()
                logger.info(f"Initial credentials: {creds.service_account_email}")
                if not creds.token:
                    logger.info("Refreshing stale credentials")
                    creds.refresh(auth_request)
            else:
                logger.info("Using local service account credentials")

            logger.info(f"Using token expiring at: {creds.expiry}")
            return creds

        except Exception as e:
            logger.error(f"Error getting credentials: {str(e)}")
            raise

    @staticmethod
    def create_signed_put_url(file_name: str, prefix_key: str = AFFIDAVIT_FOLDER_NAME) -> dict:
        """
        Return a signed URL for uploading a new file to Google Cloud Storage.

        Args:
            file_name (str): The name of the file to be uploaded.
            prefix_key (str): The prefix to be used in the GCS object key.

        Returns:
            dict: A dictionary containing the signed URL and the object key.
        """
        logger.debug("Creating signed URL for upload.")
        credentials = GoogleStoreService._get_signing_credentials()

        client = storage.Client()
        bucket_name = current_app.config["ACCOUNT_MAILER_BUCKET"]
        bucket = client.bucket(bucket_name)

        file_extension = file_name.split(".")[-1]
        key = f"{prefix_key}/{str(uuid.uuid4())}.{file_extension}"

        blob = bucket.blob(key)

        try:
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=5),
                method="PUT",
                service_account_email=credentials.service_account_email,
                access_token=credentials.token,
                content_type="application/octet-stream",
            )

            signed_url_details = {
                "preSignedUrl": signed_url,
                "key": key,
            }

            return signed_url_details
        except Exception as e:
            logger.error(f"Signing failed: {str(e)}")
            logger.error(f"Service Account: {credentials.service_account_email}")
            logger.error(f"Token valid: {credentials.valid}")
            raise

    @staticmethod
    def create_signed_get_url(key: str) -> str:
        """
        Return a signed URL for downloading an existing file from Google Cloud Storage.

        Args:
            key (str): The object key in GCS.

        Returns:
            str: A signed URL for downloading the file.
        """
        logger.debug("Creating signed URL for download.")
        credentials = GoogleStoreService._get_signing_credentials()

        client = storage.Client()
        bucket_name = current_app.config["ACCOUNT_MAILER_BUCKET"]
        bucket = client.bucket(bucket_name)

        blob = bucket.blob(key)

        try:
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=1),
                method="GET",
                service_account_email=credentials.service_account_email,
                access_token=credentials.token,
            )

            return signed_url

        except Exception as e:
            logger.error(f"Signing failed: {str(e)}")
            logger.error(f"Service Account: {credentials.service_account_email}")
            logger.error(f"Token valid: {credentials.valid}")
            raise

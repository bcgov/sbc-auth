# Copyright © 2024 Province of British Columbia
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
"""Utility functions for PDF operations."""

import base64

from auth_api.services.rest_service import RestService
from auth_api.utils.enums import AuthHeaderType, ContentType
from flask import current_app

from account_mailer.services import google_store


def get_pdf_from_report_api(pdf_payload: dict, token: str) -> bytes:
    """Get PDF from report API.

    Args:
        pdf_payload: The payload to send to the report API
        token: The authentication token

    Returns:
        bytes: The PDF content encoded in base64
    """
    report_response = RestService.post(
        endpoint=current_app.config.get("REPORT_API_BASE_URL"),
        token=token,
        auth_header_type=AuthHeaderType.BEARER,
        content_type=ContentType.JSON,
        data=pdf_payload,
        raise_for_status=True,
        additional_headers={"Accept": "application/pdf"},
    )

    if report_response.status_code != 200:
        current_app.logger.error("Failed to get pdf")
        return None

    return base64.b64encode(report_response.content)


def get_pdf_from_storage(file_name: str) -> bytes:
    """Get PDF from Google Storage.

    Args:
        file_name: The name of the file in the bucket

    Returns:
        bytes: The PDF content encoded in base64
    """
    store_blob = google_store.GoogleStoreService.download_file_from_bucket(
        current_app.config["ACCOUNT_MAILER_BUCKET"], file_name
    )

    if not store_blob:
        return None

    return base64.b64encode(store_blob)

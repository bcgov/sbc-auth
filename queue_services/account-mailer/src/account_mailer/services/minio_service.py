# Copyright © 2019 Province of British Columbia
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
"""This module is a wrapper for Minio."""

import io
import os

from flask import current_app
from minio import Minio
from structured_logging import StructuredLogging


logger = StructuredLogging.get_logger()


class MinioService:
    """Document Storage class."""

    @staticmethod
    def get_minio_file(bucket_name: str, file_name: str):
        """Return the file from Minio."""
        minio_client: Minio = MinioService._get_client()
        logger.debug(f'Get Minio file {bucket_name}/{file_name}')

        return minio_client.get_object(bucket_name, file_name)

    @staticmethod
    def put_minio_file(bucket_name: str, file_name: str, value_as_bytes: bytearray):
        """Return the file from Minio."""
        minio_client: Minio = MinioService._get_client()
        logger.debug(f'Put Minio file {bucket_name}/{file_name}')

        value_as_stream = io.BytesIO(value_as_bytes)
        minio_client.put_object(current_app.config['MINIO_BUCKET_NAME'], file_name, value_as_stream,
                                os.stat(file_name).st_size)

        return minio_client.get_object(bucket_name, file_name)

    @staticmethod
    def _get_client() -> Minio:
        """Return a minio client."""
        minio_endpoint = current_app.config['MINIO_ENDPOINT']
        minio_key = current_app.config['MINIO_ACCESS_KEY']
        minio_secret = current_app.config['MINIO_ACCESS_SECRET']
        minio_secure = current_app.config['MINIO_SECURE']

        return Minio(minio_endpoint, access_key=minio_key, secret_key=minio_secret,
                     secure=minio_secure)

    @staticmethod
    def get_minio_public_url(key: str) -> str:
        """Return a URL for uploaded document."""
        logger.debug(f'GET URL for {key}')
        minio_endpoint = current_app.config['MINIO_ENDPOINT']

        return f'https://{minio_endpoint}/public/{key}'  # noqa: E231

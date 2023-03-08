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
"""Service to invoke Rest services."""
import json
from collections.abc import Iterable
from typing import Dict

import requests
from flask import current_app, request
from requests.adapters import HTTPAdapter  # pylint:disable=ungrouped-imports
# pylint:disable=ungrouped-imports
from requests.exceptions import ConnectionError as ReqConnectionError
from requests.exceptions import ConnectTimeout, HTTPError
from urllib3.util.retry import Retry

from auth_api.exceptions import ServiceUnavailableException
from auth_api.utils.enums import AuthHeaderType, ContentType

RETRY_ADAPTER = HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1, status_forcelist=[404]))


class RestService:
    """Service to invoke Rest services which uses OAuth 2.0 implementation."""

    @staticmethod
    def _invoke(rest_method, endpoint, token=None,  # pylint: disable=too-many-arguments
                auth_header_type: AuthHeaderType = AuthHeaderType.BEARER,
                content_type: ContentType = ContentType.JSON, data=None, raise_for_status: bool = True,
                additional_headers: dict = None, generate_token: bool = True):
        """Invoke different method depending on the input."""
        # just to avoid the duplicate code for PUT and POSt
        current_app.logger.debug(f'<_invoke-{rest_method}')

        headers = {
            'Content-Type': content_type.value
        }

        if not token and generate_token:
            token = _get_token()

        if token:
            headers.update({'Authorization': auth_header_type.value.format(token)})

        if additional_headers:
            headers.update(additional_headers)

        if content_type == ContentType.JSON:
            data = json.dumps(data)

        current_app.logger.debug(f'Endpoint : {endpoint}')
        current_app.logger.debug(f'headers : {headers}')
        response = None
        try:
            invoke_rest_method = getattr(requests, rest_method)
            response = invoke_rest_method(endpoint, data=data, headers=headers,
                                          timeout=current_app.config.get('CONNECT_TIMEOUT', 60))
            if raise_for_status:
                response.raise_for_status()
        except (ReqConnectionError, ConnectTimeout) as exc:
            current_app.logger.error('---Error on POST---')
            current_app.logger.error(exc)
            raise ServiceUnavailableException(exc) from exc
        except HTTPError as exc:
            current_app.logger.error(f"HTTPError on POST with status code {response.status_code if response else ''}")
            if response and response.status_code >= 500:
                raise ServiceUnavailableException(exc) from exc
            raise exc
        finally:
            RestService.__log_response(response)

        current_app.logger.debug('>post')
        return response

    @staticmethod
    def __log_response(response):
        if response is not None:
            current_app.logger.info(f'Response Headers {response.headers}')
            if response.headers and isinstance(response.headers, Iterable) and \
                    'Content-Type' in response.headers and \
                    response.headers['Content-Type'] == ContentType.JSON.value:
                current_app.logger.info(f"response : {response.text if response else ''}")

    @staticmethod
    def post(endpoint, token=None,  # pylint: disable=too-many-arguments
             auth_header_type: AuthHeaderType = AuthHeaderType.BEARER,
             content_type: ContentType = ContentType.JSON, data=None, raise_for_status: bool = True,
             additional_headers: dict = None, generate_token: bool = True):
        """POST service."""
        current_app.logger.debug('<post')
        return RestService._invoke('post', endpoint, token, auth_header_type, content_type, data, raise_for_status,
                                   additional_headers, generate_token)

    @staticmethod
    def put(endpoint, token=None,  # pylint: disable=too-many-arguments
            auth_header_type: AuthHeaderType = AuthHeaderType.BEARER,
            content_type: ContentType = ContentType.JSON, data=None, raise_for_status: bool = True):
        """POST service."""
        current_app.logger.debug('<post')
        return RestService._invoke('put', endpoint, token, auth_header_type, content_type, data, raise_for_status)

    @staticmethod
    def patch(endpoint, token=None,  # pylint: disable=too-many-arguments
              auth_header_type: AuthHeaderType = AuthHeaderType.BEARER,
              content_type: ContentType = ContentType.JSON, data=None, raise_for_status: bool = True,
              additional_headers: dict = None, generate_token=True):
        """Patch service."""
        current_app.logger.debug('<patch')
        return RestService._invoke('patch', endpoint, token, auth_header_type, content_type, data, raise_for_status,
                                   additional_headers, generate_token)

    @staticmethod
    def delete(endpoint, token=None,  # pylint: disable=too-many-arguments
               auth_header_type: AuthHeaderType = AuthHeaderType.BEARER,
               content_type: ContentType = ContentType.JSON, data=None, raise_for_status: bool = True,
               additional_headers: dict = None, generate_token=True):
        """Patch service."""
        current_app.logger.debug('<delete')
        return RestService._invoke('delete', endpoint, token, auth_header_type, content_type, data, raise_for_status,
                                   additional_headers, generate_token)

    @staticmethod
    def get(endpoint, token=None,  # pylint: disable=too-many-arguments
            auth_header_type: AuthHeaderType = AuthHeaderType.BEARER,
            content_type: ContentType = ContentType.JSON, retry_on_failure: bool = False,
            additional_headers: Dict = None):
        """GET service."""
        current_app.logger.debug('<GET')

        headers = {
            'Content-Type': content_type.value
        }
        if additional_headers:
            headers.update(additional_headers)

        if token:
            headers['Authorization'] = auth_header_type.value.format(token)

        current_app.logger.debug(f'Endpoint : {endpoint}')
        current_app.logger.debug(f'headers : {headers}')
        session = requests.Session()
        if retry_on_failure:
            session.mount(endpoint, RETRY_ADAPTER)
        response = None
        try:
            response = session.get(endpoint, headers=headers, timeout=current_app.config.get('CONNECT_TIMEOUT', 60))
            response.raise_for_status()
        except (ReqConnectionError, ConnectTimeout) as exc:
            current_app.logger.error('---Error on GET---')
            current_app.logger.error(exc)
            raise ServiceUnavailableException(exc) from exc
        except HTTPError as exc:
            current_app.logger.error(f"HTTPError on GET with status code {response.status_code if response else ''}")
            if response and response.status_code >= 500:
                raise ServiceUnavailableException(exc) from exc
            raise exc
        finally:
            current_app.logger.debug(response.headers if response else 'Empty Response Headers')
            current_app.logger.info(f"response : {response.text if response else ''}")

        current_app.logger.debug('>GET')
        return response

    @staticmethod
    def get_service_account_token(config_id='KEYCLOAK_SERVICE_ACCOUNT_ID', config_secret='KEYCLOAK_SERVICE_ACCOUNT_SECRET') -> str:
        """Generate a service account token."""
        kc_service_id = current_app.config.get(config_id)
        kc_secret = current_app.config.get(config_secret)
        issuer_url = current_app.config.get('JWT_OIDC_ISSUER')
        token_url = issuer_url + '/protocol/openid-connect/token'
        auth_response = requests.post(token_url, auth=(kc_service_id, kc_secret), headers={
            'Content-Type': ContentType.FORM_URL_ENCODED.value}, data='grant_type=client_credentials',
                timeout=current_app.config.get('CONNECT_TIMEOUT', 60))
        auth_response.raise_for_status()
        return auth_response.json().get('access_token')


def _get_token() -> str:
    token: str = request.headers['Authorization'] if request and 'Authorization' in request.headers else None
    return token.replace('Bearer ', '') if token else None

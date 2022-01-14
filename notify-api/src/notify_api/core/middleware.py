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
"""Generic middleware."""
import json
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from notify_api.db.database import SESSION


logger = logging.getLogger(__name__)


async def response_middleware(request: Request, call_next):
    """Override response message for autherencation error (401)."""
    response = await call_next(request)
    # do something() instead that line to convert Request -> JSONResponse
    resp_body = [section async for section in response.__dict__['body_iterator']]
    # Repairing FastAPI response
    response.__setattr__('body_iterator', AsyncIteratorWrapper(resp_body))

    # Formatting response body for logging
    try:
        resp_body = json.loads(resp_body[0].decode())
    except ValueError:
        if isinstance(resp_body, list):
            resp_body = str(resp_body[0].decode())
        else:
            resp_body = str(resp_body)

    # Overwrite status code from 400 to 401
    if resp_body == 'Signature has expired':
        response = JSONResponse({'errors': resp_body}, status_code=401)
    return response


async def session_middleware(request: Request, call_next):
    """Close the session after each request, thus rolling back any not committed transactions."""
    added = False
    try:
        if not hasattr(request.state, 'session'):
            request.state.session = SESSION()
            added = True
        response = await call_next(request)
    finally:
        if added:
            # Only close a session if we added it, useful for testing
            request.state.session.close()
    return response


class SessionMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """Class-based version of session_middleware."""

    async def dispatch(
            self,
            request: Request,
            call_next
    ) -> Response:
        """Dispatch function."""
        return await session_middleware(request, call_next)


class ResponseMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """Class-based version of response_middleware."""

    async def dispatch(
            self,
            request: Request,
            call_next
    ) -> Response:
        """Dispatch function."""
        return await response_middleware(request, call_next)


class AsyncIteratorWrapper:
    """Get response body."""

    def __init__(self, obj):
        """inti."""
        self._it = iter(obj)

    def __aiter__(self):
        """aiter."""
        return self

    async def __anext__(self):
        """anext."""
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value

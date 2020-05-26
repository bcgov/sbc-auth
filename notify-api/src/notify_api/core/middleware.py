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
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from notify_api.db.database import SESSION


logger = logging.getLogger(__name__)


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


class SessionMiddleware(BaseHTTPMiddleware):
    """Class-based version of session_middleware."""

    async def dispatch(
            self,
            request: Request,
            call_next
    ) -> Response:
        """Dispatch function."""
        return await session_middleware(request, call_next)

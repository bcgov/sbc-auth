""" Generic middleware """
import logging

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from notify_api.db.database import SESSION


PAYLOAD_HEADER_PREFIX = 'x-payload-'

logger = logging.getLogger(__name__)


async def session_middleware(request: Request, call_next):
    """
    Close the session after each request, thus rolling back any
    not committed transactions.  The session is also stored as part
    of the request via request.state.session.
    """
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
    """
    Class-based version of session_middleware
    """
    async def dispatch(
            self,
            request: Request,
            call_next
    ) -> Response:
        return await session_middleware(request, call_next)


class UpstreamPayloadMiddleware(BaseHTTPMiddleware):
    """ Set payload from upstream request headers.
    NOTE: there must be an upstream service (like an API Gateway) to
    ensure these headers are trusted.  Otherwise the client could set
    any desired permissions.
    """

    def __init__(
            self,
            app: ASGIApp,
            header_prefix=PAYLOAD_HEADER_PREFIX,
    ):
        super().__init__(app=app)
        self.header_prefix = header_prefix

    async def dispatch(
            self,
            request: Request,
            call_next
    ) -> Response:
        payload = {}
        for header_name in request.headers:
            if header_name.startswith(self.header_prefix):
                name = header_name[len(self.header_prefix):]
                value = request.headers.getlist(header_name)
                if len(value) == 1:
                    payload[name] = value[0]
                else:
                    payload[name] = value
        request.state.payload = payload
        return await call_next(request)


class JwtMiddleware(BaseHTTPMiddleware):
    """ Middleware to decode a JWT (if present)
    and add the results to request.state.payload
    """

    def __init__(
            self,
            app: ASGIApp,
            secret: str,
            cookie_name: str = 'jwt',
            algorithms=None,
            **kwargs,
    ):
        super().__init__(app=app)
        self.secret = secret
        self.cookie_name = cookie_name
        self.algorithms = algorithms or ['HS256', 'HS512']
        self.kwargs = kwargs

    async def dispatch(
            self, request: Request,
            call_next
    ) -> Response:
        token = request.cookies.get(self.cookie_name)
        if token:
            try:
                payload = jwt.decode(
                    token,
                    key=self.secret,
                    algorithms=self.algorithms,
                    **self.kwargs
                )
                request.state.payload = payload
            except jwt.exceptions.InvalidTokenError as token_error:
                logger.info('JWT decode error: %s', str(token_error))
        else:
            logging.debug('%s: No JWT', str(request.url))

        return await call_next(request)

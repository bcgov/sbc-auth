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
""" The Notify Serive. """
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from sqlalchemy.engine import Connection, Engine, create_engine
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import BaseRoute
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from notify_api.core import config as AppConfig
from notify_api.core.errors import http_422_error_handler, http_error_handler
from notify_api.core.middleware import session_middleware
from notify_api.db.database import SESSION as db_session
from notify_api.resources import ROUTER as api_router
from notify_api.resources import ops


class NotifyAPI(FastAPI):
    """ Application class for Mitto """

    def __init__(
            self,
            bind: Union[str, Engine, Connection, None],
            debug: bool = False,
            routes: List[BaseRoute] = None,
            template_directory: str = None,
            title: str = 'Notify API',
            description: str = '',
            version: str = '1.0.0',
            openapi_url: Optional[str] = '/openapi.json',
            openapi_prefix: str = '',
            docs_url: Optional[str] = '/docs',
            redoc_url: Optional[str] = '/redoc',
            **extra: Dict[str, Any],
    ):  # pylint: disable=too-many-arguments
        super().__init__(
            debug=debug,
            routes=routes,
            template_directory=template_directory,
            title=title,
            description=description,
            version=version,
            openapi_url=openapi_url,
            openapi_prefix=openapi_prefix,
            docs_url=docs_url,
            redoc_url=redoc_url,
            **extra
        )
        if bind is not None:
            if isinstance(bind, str):
                self.bind = create_engine(bind, pool_pre_ping=True)
            else:
                self.bind = bind
            db_session.configure(bind=self.bind)
        else:
            self.bind = None

    @property
    def db_session(self):
        """ Convenience property for the global Session """
        return db_session()

    def setup(self) -> None:
        """ Override setup() to not add openapi_prefix to openapi_url """
        if self.openapi_url:
            async def openapi(_req: Request) -> JSONResponse:
                return JSONResponse(self.openapi())

            self.add_route(self.openapi_url, openapi, include_in_schema=False)
            # REMOVED: openapi_url = self.openapi_prefix + self.openapi_url
        if self.openapi_url and self.docs_url:

            async def swagger_ui_html(_req: Request) -> HTMLResponse:
                return get_swagger_ui_html(
                    openapi_url=self.openapi_url,
                    title=self.title + ' - Swagger UI',
                    oauth2_redirect_url=self.swagger_ui_oauth2_redirect_url,
                )

            self.add_route(
                self.docs_url, swagger_ui_html, include_in_schema=False
            )

            self.include_router(api_router, prefix=AppConfig.API_V1_STR)
            self.include_router(ops.ROUTER, prefix='/ops', tags=['ops'])

            if self.swagger_ui_oauth2_redirect_url:
                async def swagger_ui_redirect(_req: Request) -> HTMLResponse:
                    return get_swagger_ui_oauth2_redirect_html()

                self.add_route(
                    self.swagger_ui_oauth2_redirect_url,
                    swagger_ui_redirect,
                    include_in_schema=False,
                )
        if self.openapi_url and self.redoc_url:
            async def redoc_html(_req: Request) -> HTMLResponse:
                return get_redoc_html(
                    openapi_url=self.openapi_url, title=self.title + ' - ReDoc'
                )

            self.add_route(self.redoc_url, redoc_html, include_in_schema=False)
        self.add_exception_handler(HTTPException, http_error_handler)
        self.add_exception_handler(HTTP_422_UNPROCESSABLE_ENTITY, http_422_error_handler)
        # ADDED
        self.add_default_middleware()

    def add_default_middleware(self) -> None:
        """ Add any default middleware """
        self.add_middleware(BaseHTTPMiddleware, dispatch=session_middleware)

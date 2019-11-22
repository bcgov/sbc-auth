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
"""error setup."""
from collections.abc import Iterable

from fastapi.openapi.constants import REF_PREFIX
from fastapi.openapi.utils import (
    validation_error_definition,
    validation_error_response_definition,
)
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY


async def http_error_handler(request: Request,  # pylint: disable=unused-argument
                             exc: HTTPException) -> JSONResponse:
    """Handler for error to transform default pydantic error object to gothinkster format."""
    return JSONResponse({'errors': [exc.detail]}, status_code=exc.status_code)


async def http_422_error_handler(request: Request,  # pylint: disable=unused-argument
                                 exc: HTTPException) -> JSONResponse:
    """Handler for 422 error to transform default pydantic error object to gothinkster format."""

    errors = {'body': []}

    if isinstance(exc.detail, Iterable) and not isinstance(exc.detail, str):
        for error in exc.detail:
            error_name = '.'.join(error['loc'][1:])  # remove 'body' from path to invalid element
            errors['body'].append({error_name: error['msg']})
    else:
        errors['body'].append(exc.detail)

    return JSONResponse({'errors': errors}, status_code=HTTP_422_UNPROCESSABLE_ENTITY)


validation_error_definition['properties'] = {
    'body': {'title': 'Body', 'type': 'array', 'items': {'type': 'string'}}
}

validation_error_response_definition['properties'] = {
    'errors': {
        'title': 'Errors',
        'type': 'array',
        'items': {'$ref': REF_PREFIX + 'ValidationError'},
    }
}

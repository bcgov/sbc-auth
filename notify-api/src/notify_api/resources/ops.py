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
"""API endpoints for managing a notify resource."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import exc, text
from starlette.responses import JSONResponse

from notify_api.db.database import get_db


ROUTER = APIRouter()

SQL = text('select 1')


@ROUTER.get('/healthz')
async def healthz(db_session: Session = Depends(get_db)):
    """Determines if the service and required dependencies are still working.

    This could be thought of as a heartbeat for the service.
    """
    try:
        db_session.execute(SQL)
    except exc.SQLAlchemyError:
        return JSONResponse(status_code=500, content={'message': 'api is down'})

    # made it here, so all checks passed
    return JSONResponse(status_code=200, content={'message': 'api is healthy'})


@ROUTER.get('/readyz')
async def readyz():
    """Return a JSON object that identifies if the service is setupAnd ready to work."""
    # TODO: add a poll to the DB when called
    return JSONResponse(status_code=200, content={'message': 'api is ready'})

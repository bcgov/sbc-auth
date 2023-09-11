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
"""Endpoints to check and manage the health of the service."""
from flask import Blueprint
from sqlalchemy import exc, text

from auth_api.models import db


bp = Blueprint('OPS', __name__, url_prefix='/ops')

SQL = text('select 1')


@bp.route('healthz', methods=['GET'])
def get_ops_healthz():
    """Return a JSON object stating the health of the Service and dependencies."""
    try:
        db.engine.execute(SQL)
    except exc.SQLAlchemyError:
        return {'message': 'api is down'}, 500

    # made it here, so all checks passed
    return {'message': 'api is healthy'}, 200


@bp.route('readyz', methods=['GET'])
def get_ops_readyz():
    """Return a JSON object that identifies if the service is setupAnd ready to work."""
    # TODO: add a poll to the DB when called
    return {'message': 'api is ready'}, 200
